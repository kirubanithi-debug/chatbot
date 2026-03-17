import re

SIMPLE_QUESTION_SUGGESTIONS = [
    'Hi',
    'What can you do?',
    'How to file FIR?',
    'Cyber complaint website?',
    'Police emergency number?',
    'Women helpline number?',
    'No road in my street',
    'Drainage overflow near my house',
    'Neighbor encroached my land',
    'Illegal construction near my home',
    'Street light not working in my area',
    'Water supply issue in my street',
    'Caste abuse in public place',
    'Marriage and dowry harassment',
    'Divorce case with husband/wife',
    'College fee paid but no facilities',
    'Hospital denied treatment',
    'Private company salary due',
    'Private bus overcharge complaint',
    'Government bus unsafe service',
    'Accident injury compensation',
    'Agriculture crop loss compensation',
    'Mobile stolen and SIM misuse',
    'Wrong EB electricity bill',
    'Frequent power cut in my area',
    'Low voltage in my street',
    'Bad touch complaint',
    'Chain snatching complaint',
    'Illegal tree cutting complaint',
    'Fake doctor complaint',
    'Fake medicine complaint',
    'No helmet traffic fine',
    'Natural disaster relief complaint',
    'Women safety harassment complaint',
    'Men safety blackmail complaint',
    'Child safety abuse complaint',
    'Elder safety maintenance complaint',
    'No signal and call drop complaint',
    'Home loan not approved by bank',
    'Family land dispute with brother',
    'Family vehicle ownership dispute',
    'House owner forcing tenant to vacate',
    'House owner denied water supply',
    'Noise pollution complaint',
    'Air pollution complaint',
    'Land pollution complaint',
    'Political election threat complaint',
    'Panchayat no water tank complaint',
    'Town municipality civic complaint',
    'City corporation civic complaint',
    'Temple trust money misuse complaint',
    'Temple religious insult complaint',
    'Garbage was not collected complaint',
    'Drainage was not clean complaint',
    'MLA/MP not responding complaint',
]


def _norm(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip()


def _word_present(word: str, text: str) -> bool:
    """Check if *word* appears as a whole word (not a substring of another word)."""
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))


def _build_response(next_steps: str) -> str:
    return (
        'LAW: General Legal Guidance\n'
        'SECTION: Basic Help\n'
        'PUNISHMENT: Not applicable\n'
        f'NEXT STEPS: {next_steps}\n'
        'DISCLAIMER: Consult lawyer'
    )


def get_simple_qa_response(query: str) -> str | None:
    q = _norm(query)

    if any(_word_present(word, q) for word in ['hi', 'hello', 'hey']):
        return _build_response(
            '1. Ask your issue in one sentence (example: bike stolen). '
            '2. Add place/time details. 3. Follow legal steps shown in response.'
        )

    if ('what can you do' in q) or ('help' in q and 'legal' in q):
        return _build_response(
            '1. Ask crime/civil/labour/cyber issue in plain words. '
            '2. Get law section, punishment, and next steps. '
            '3. For urgent danger, contact police immediately.'
        )

    if ('how to file fir' in q) or ('file fir' in q and 'how' in q):
        return _build_response(
            '1. Visit nearest police station or use state e-FIR portal. '
            '2. Provide clear incident facts, date, place, suspect details, and evidence. '
            '3. Take FIR number/copy and track investigation status.'
        )

    if ('cyber complaint' in q) or ('cybercrime' in q) or ('online complaint' in q):
        return _build_response(
            '1. Use cybercrime.gov.in. 2. Upload screenshots, transaction IDs, and account details. '
            '3. Also file FIR and inform bank/payment provider quickly.'
        )

    if ('police emergency' in q) or ('emergency number' in q) or ('call police' in q):
        return _build_response(
            '1. Dial 112 (India emergency response support system). '
            '2. Share exact location and danger details. 3. Preserve evidence for FIR.'
        )

    if ('women helpline' in q) or ('women help number' in q):
        return _build_response(
            '1. Dial 181 (women helpline, state availability may vary). '
            '2. For immediate danger dial 112. 3. File police complaint and preserve evidence.'
        )

    if any(word in q for word in ['thanks', 'thank you']):
        return _build_response('1. Ask next legal question any time. 2. Save important documents/evidence. 3. Consult a lawyer for case-specific advice.')

    return None


def get_default_guidance_response(query: str) -> str:
    q = _norm(query)
    return _build_response(
        f"1. I could not map this clearly: '{q[:120]}'. "
        "2. Rephrase with incident type + place + time (example: 'phone stolen in bus at Chennai'). "
        "3. If urgent danger, call 112 and file FIR at nearest police station."
    )
