import requests
from celery import shared_task
from django.conf import settings

from .models import LegalQuery
from .query_understanding import understand_user_query
from .rag_setup import find_best_legal_entry, get_context
from .simple_qa import get_default_guidance_response, get_simple_qa_response

SYSTEM_PROMPT = """You are Indian Law Expert. Answer EXACTLY:
LAW: IPC 378
SECTION: Theft
PUNISHMENT: 3 years jail + fine
NEXT STEPS: 1.FIR 2.Evidence 3.Followup
DISCLAIMER: Consult lawyer

Use ONLY RAG context. No context = 'Consult lawyer'"""


def _is_placeholder(text: str) -> bool:
    value = (text or '').strip().lower()
    return any(
        token in value
        for token in [
            'not explicitly available',
            'not available',
            'not applicable',
            'consult lawyer',
            'n/a',
            'na',
        ]
    )


def _safe_punishment(value: str) -> str:
    cleaned = (value or '').strip()
    if not cleaned or _is_placeholder(cleaned):
        return 'No direct penal punishment stated in this provision; follow statutory remedy/procedure.'
    return cleaned


def _safe_next_steps(value: str) -> str:
    cleaned = (value or '').strip()
    if not cleaned:
        return '1. Preserve all records/evidence. 2. File complaint before the competent authority/police. 3. Consult lawyer for case-specific action.'
    return cleaned


def _response_block(law: str, section: str, punishment: str, next_steps: str) -> str:
    return (
        f"LAW: {(law or 'Consult lawyer').strip()}\n"
        f"SECTION: {(section or 'Consult lawyer').strip()}\n"
        f"PUNISHMENT: {_safe_punishment(punishment)}\n"
        f"NEXT STEPS: {_safe_next_steps(next_steps)}\n"
        "DISCLAIMER: Consult lawyer"
    )


def _extract_field(context: str, label: str) -> str:
    prefix = f"{label}:"
    for line in context.splitlines():
        if line.strip().startswith(prefix):
            return line.split(':', 1)[1].strip()
    return ''


def format_response_from_context(context: str) -> str:
    law = _extract_field(context, 'LAW')
    section = _extract_field(context, 'SECTION')
    punishment = _extract_field(context, 'PUNISHMENT')
    next_steps = _extract_field(context, 'NEXT STEPS')

    if not law or not section:
        return _response_block(
            law='Consult lawyer',
            section='Consult lawyer',
            punishment='',
            next_steps='',
        )

    return _response_block(
        law=law,
        section=section,
        punishment=punishment,
        next_steps=next_steps,
    )


def format_response_from_entry(entry: dict) -> str:
    return _response_block(
        law=str(entry.get('law', '')).strip() or 'Consult lawyer',
        section=str(entry.get('section', '')).strip() or 'Consult lawyer',
        punishment=str(entry.get('punishment', '')).strip(),
        next_steps=str(entry.get('next_steps', '')).strip(),
    )


def normalize_ai_response(ai_response: str, entry: dict | None = None, context: str = '') -> str:
    base = ai_response or ''
    law = _extract_field(base, 'LAW')
    section = _extract_field(base, 'SECTION')
    punishment = _extract_field(base, 'PUNISHMENT')
    next_steps = _extract_field(base, 'NEXT STEPS')

    if entry:
        law = law or str(entry.get('law', '')).strip()
        section = section or str(entry.get('section', '')).strip()
        punishment = punishment or str(entry.get('punishment', '')).strip()
        next_steps = next_steps or str(entry.get('next_steps', '')).strip()

    if context:
        law = law or _extract_field(context, 'LAW')
        section = section or _extract_field(context, 'SECTION')
        punishment = punishment or _extract_field(context, 'PUNISHMENT')
        next_steps = next_steps or _extract_field(context, 'NEXT STEPS')

    return _response_block(law=law, section=section, punishment=punishment, next_steps=next_steps)


def build_prompt(user_query: str, context: str) -> str:
    if not context.strip():
        return (
            f"{SYSTEM_PROMPT}\n\n"
            "CONTEXT:\nNone\n\n"
            f"USER QUERY: {user_query}\n\n"
            "Return exactly:\nDISCLAIMER: Consult lawyer"
        )

    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Strict output format:\n"
        "LAW: ...\n"
        "SECTION: ...\n"
        "PUNISHMENT: ...\n"
        "NEXT STEPS: 1... 2... 3...\n"
        "DISCLAIMER: Consult lawyer\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"USER QUERY: {user_query}"
    )


def ask_ollama(prompt: str) -> str:
    endpoint = f"{settings.OLLAMA_HOST}/api/generate"
    # Fast health probe prevents long retry/backoff cascades when Ollama is down.
    health = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=1.2)
    health.raise_for_status()
    payload = {
        'model': settings.OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False,
    }
    response = requests.post(endpoint, json=payload, timeout=45)
    response.raise_for_status()
    data = response.json()
    return data.get('response', '').strip()


@shared_task

def process_legal_query(legal_query_id: int) -> None:
    try:
        legal_query = LegalQuery.objects.get(id=legal_query_id)
    except LegalQuery.DoesNotExist:
        return

    simple_answer = get_simple_qa_response(legal_query.user_query)
    if simple_answer:
        legal_query.ai_response = simple_answer
        legal_query.status = 'completed'
        legal_query.save(update_fields=['ai_response', 'status', 'updated_at'])
        return

    understanding = understand_user_query(legal_query.user_query)
    lookup_query = understanding.enriched_query or legal_query.user_query

    entry = find_best_legal_entry(lookup_query)
    if entry and entry.get('confidence', 0) >= 0.42:
        legal_query.ai_response = format_response_from_entry(entry)
        legal_query.status = 'completed'
        legal_query.save(update_fields=['ai_response', 'status', 'updated_at'])
        return

    context = get_context(lookup_query, k=3)

    if not context.strip() and entry:
        context = (
            f"LAW: {entry.get('law', '')}\n"
            f"SECTION: {entry.get('section', '')}\n"
            f"PUNISHMENT: {entry.get('punishment', '')}\n"
            f"NEXT STEPS: {entry.get('next_steps', '')}\n"
            f"KEYWORDS: {entry.get('keywords', '')}"
        )

    if not context.strip():
        legal_query.ai_response = get_default_guidance_response(legal_query.user_query)
        legal_query.status = 'completed'
        legal_query.save(update_fields=['ai_response', 'status', 'updated_at'])
        return

    prompt = build_prompt(user_query=legal_query.user_query, context=context)
    try:
        ai_response = ask_ollama(prompt)
    except requests.RequestException:
        ai_response = format_response_from_entry(entry) if entry else format_response_from_context(context)

    if not ai_response.strip() or 'LAW:' not in ai_response:
        ai_response = format_response_from_entry(entry) if entry else format_response_from_context(context)

    ai_response = normalize_ai_response(ai_response=ai_response, entry=entry, context=context)

    legal_query.ai_response = ai_response or get_default_guidance_response(legal_query.user_query)
    legal_query.status = 'completed'
    legal_query.save(update_fields=['ai_response', 'status', 'updated_at'])
