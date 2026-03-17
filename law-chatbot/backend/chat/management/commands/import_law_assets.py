import csv
import json
import re
import sqlite3
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand


REQUIRED_COLUMNS = ['law', 'section', 'punishment', 'next_steps', 'keywords']

LOW_VALUE_SECTION_TERMS = {
    'short title',
    'commencement',
    'extent',
    'definitions',
    'repeal',
    'application of act',
}

STOPWORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'from', 'into', 'under', 'shall', 'may', 'all',
    'any', 'are', 'was', 'were', 'has', 'have', 'had', 'not', 'its', 'their', 'his', 'her', 'him',
    'she', 'himself', 'herself', 'they', 'them', 'act', 'section', 'article', 'code', 'law',
}


def _clean_text(text: str) -> str:
    text = str(text or '').replace('\u00a0', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _is_low_value_section(title: str) -> bool:
    t = _clean_text(title).lower()
    return any(term in t for term in LOW_VALUE_SECTION_TERMS)


def _extract_punishment(description: str) -> str:
    text = _clean_text(description)
    if not text:
        return 'Punishment not explicitly available in imported source text.'

    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        s_l = s.lower()
        if any(k in s_l for k in ['punish', 'imprison', 'fine', 'liable', 'penalty', 'death', 'life imprisonment']):
            return _clean_text(s)

    m = re.search(r'(shall be punish[^.]*\.|whoever[^.]*shall be punish[^.]*\.)', text, flags=re.IGNORECASE)
    if m:
        return _clean_text(m.group(1))

    return 'Punishment not explicitly available in imported source text.'


def _default_next_steps(law_name: str) -> str:
    l = law_name.lower()
    if any(x in l for x in ['ipc', 'bns', 'crpc', 'it act', 'motor vehicles', 'ndps']):
        return '1. Preserve evidence and incident details. 2. File FIR/complaint with police or cyber cell. 3. Consult lawyer and track case status.'
    if any(x in l for x in ['income tax', 'gst', 'fema', 'rera', 'banking']):
        return '1. Preserve notices, records and payment documents. 2. File response/complaint before competent authority. 3. Consult subject-matter lawyer/CA.'
    if any(x in l for x in ['constitution', 'cpc', 'evidence']):
        return '1. Identify proper legal forum and remedy. 2. Preserve documentary evidence. 3. Consult lawyer for case strategy.'
    return '1. Preserve supporting documents and evidence. 2. File complaint before proper authority. 3. Consult lawyer for next legal remedy.'


def _generate_keywords(law: str, section: str, description: str) -> str:
    src = f"{law} {section} {description}".lower()
    tokens = re.findall(r'[a-z0-9]+', src)
    out = []
    seen = set()
    for tok in tokens:
        if len(tok) < 3 or tok in STOPWORDS:
            continue
        if tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
        if len(out) >= 25:
            break
    return ' '.join(out)


def _record(law: str, section: str, description: str) -> dict:
    punishment = _extract_punishment(description)
    return {
        'law': _clean_text(law),
        'section': _clean_text(section),
        'punishment': punishment,
        'next_steps': _default_next_steps(law),
        'keywords': _generate_keywords(law, section, description),
    }


def _parse_generic_json(path: Path, law_name: str, section_key: str, title_key: str, desc_key: str):
    out = []
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    for row in data:
        if not isinstance(row, dict):
            continue
        section_no = row.get(section_key, '')
        title = row.get(title_key, '')
        desc = row.get(desc_key, '')
        if not title and not desc:
            continue
        if _is_low_value_section(title):
            continue
        section = f"Section {section_no} - {_clean_text(title)}" if section_no != '' else _clean_text(title)
        out.append(_record(law_name, section, str(desc)))
    return out


def _parse_constitution_json(path: Path):
    out = []
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    for row in data:
        if not isinstance(row, dict):
            continue
        article = row.get('article', '')
        title = row.get('title', '')
        desc = row.get('description', '')
        if not title and not desc:
            continue
        section = f"Article {article} - {_clean_text(title)}"
        out.append(_record('Constitution of India', section, str(desc)))
    return out


def _parse_hma_json(path: Path):
    out = []
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    for row in data:
        if not isinstance(row, dict):
            continue
        value = row.get('chapter,section,section_title,section_desc', '')
        value = _clean_text(value)
        if not value:
            continue
        try:
            parsed = next(csv.reader([value]))
        except Exception:
            continue
        if len(parsed) < 4:
            continue
        section_no = parsed[1]
        title = parsed[2]
        desc = ','.join(parsed[3:])
        if _is_low_value_section(title):
            continue
        section = f"Section {section_no} - {_clean_text(title)}"
        out.append(_record('Hindu Marriage Act, 1955', section, desc))
    return out


def _parse_cpc_like_json(path: Path, law_name: str):
    out = []
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    for row in data:
        if not isinstance(row, dict):
            continue
        section_no = row.get('section', '')
        title = row.get('title', '')
        desc = row.get('description', '')
        if not title and not desc:
            continue
        if _is_low_value_section(title):
            continue
        section = f"Section {section_no} - {_clean_text(title)}"
        out.append(_record(law_name, section, str(desc)))
    return out


def _parse_sqlite_tables(path: Path, table_law_map: dict):
    out = []
    con = sqlite3.connect(path)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    for table, law_name in table_law_map.items():
        if table not in tables:
            continue
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info('{table}')").fetchall()]
        if not cols:
            continue
        rows = cur.execute(f"SELECT * FROM '{table}'").fetchall()
        col_idx = {c: i for i, c in enumerate(cols)}

        for r in rows:
            if 'section_title' in col_idx:
                sec_no = r[col_idx.get('section', col_idx.get('Section', -1))] if ('section' in col_idx or 'Section' in col_idx) else ''
                title = r[col_idx['section_title']]
                desc = r[col_idx.get('section_desc', col_idx.get('description', -1))] if ('section_desc' in col_idx or 'description' in col_idx) else ''
            elif 'title' in col_idx and 'description' in col_idx:
                sec_no = r[col_idx.get('section', col_idx.get('article', -1))] if ('section' in col_idx or 'article' in col_idx) else ''
                title = r[col_idx['title']]
                desc = r[col_idx['description']]
            else:
                continue

            title = _clean_text(title)
            if not title or _is_low_value_section(title):
                continue
            section_prefix = 'Article' if 'constitution' in law_name.lower() else 'Section'
            section = f"{section_prefix} {sec_no} - {title}" if sec_no != '' else title
            out.append(_record(law_name, section, str(desc)))

    con.close()
    return out


def _dedupe_records(records: list[dict]) -> list[dict]:
    merged = {}
    for rec in records:
        key = (rec['law'].strip().lower(), rec['section'].strip().lower())
        if key not in merged:
            merged[key] = rec
            continue
        prev = merged[key]
        if len(rec.get('punishment', '')) > len(prev.get('punishment', '')):
            prev['punishment'] = rec['punishment']
        if len(rec.get('keywords', '')) > len(prev.get('keywords', '')):
            prev['keywords'] = rec['keywords']
        if len(rec.get('next_steps', '')) > len(prev.get('next_steps', '')):
            prev['next_steps'] = rec['next_steps']

    return list(merged.values())


class Command(BaseCommand):
    help = 'Import uploaded law assets (JSON/DB/CSV) into data/legal_sections.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--assets-dir',
            default='/home/kiruba/legal chatbot/assects',
            help='Directory containing uploaded legal assets',
        )
        parser.add_argument(
            '--output-csv',
            default='data/legal_sections.csv',
            help='Output CSV path relative to backend root',
        )

    def handle(self, *args, **options):
        assets_dir = Path(options['assets_dir'])
        output_csv = Path(options['output_csv'])

        if not assets_dir.exists():
            self.stderr.write(self.style.ERROR(f'Assets dir not found: {assets_dir}'))
            return

        records = []

        json_jobs = [
            ('ipc.json', 'Indian Penal Code (IPC)', 'Section', 'section_title', 'section_desc', 'generic'),
            ('crpc.json', 'Code of Criminal Procedure (CrPC)', 'section', 'section_title', 'section_desc', 'generic'),
            ('iea.json', 'Indian Evidence Act', 'section', 'section_title', 'section_desc', 'generic'),
            ('nia.json', 'Negotiable Instruments Act', 'section', 'section_title', 'section_desc', 'generic'),
            ('cpc.json', 'Code of Civil Procedure (CPC)', 'section', 'title', 'description', 'cpc_like'),
            ('ida.json', 'Indian Divorce Act', 'section', 'title', 'description', 'cpc_like'),
            ('MVA.json', 'Motor Vehicles Act, 1988', 'section', 'title', 'description', 'cpc_like'),
        ]

        for filename, law, s_key, t_key, d_key, kind in json_jobs:
            path = assets_dir / filename
            if not path.exists():
                continue
            if kind == 'generic':
                part = _parse_generic_json(path, law, s_key, t_key, d_key)
            else:
                part = _parse_cpc_like_json(path, law)
            records.extend(part)
            self.stdout.write(f'Imported {len(part)} from {filename}')

        path = assets_dir / 'constitution_of_india.json'
        if path.exists():
            part = _parse_constitution_json(path)
            records.extend(part)
            self.stdout.write(f'Imported {len(part)} from constitution_of_india.json')

        path = assets_dir / 'hma.json'
        if path.exists():
            part = _parse_hma_json(path)
            records.extend(part)
            self.stdout.write(f'Imported {len(part)} from hma.json')

        db_path = assets_dir / 'IndiaLaw.db'
        if db_path.exists():
            part = _parse_sqlite_tables(
                db_path,
                {
                    'IPC': 'Indian Penal Code (IPC)',
                    'NIA': 'Negotiable Instruments Act',
                    'IEA': 'Indian Evidence Act',
                    'CRPC': 'Code of Criminal Procedure (CrPC)',
                    'HMA': 'Hindu Marriage Act, 1955',
                    'CPC': 'Code of Civil Procedure (CPC)',
                    'IDA': 'Indian Divorce Act',
                    'MVA': 'Motor Vehicles Act, 1988',
                },
            )
            records.extend(part)
            self.stdout.write(f'Imported {len(part)} from IndiaLaw.db')

        db_path = assets_dir / 'COI.db'
        if db_path.exists():
            part = _parse_sqlite_tables(db_path, {'Constitution of India': 'Constitution of India'})
            records.extend(part)
            self.stdout.write(f'Imported {len(part)} from COI.db')

        csv_path = assets_dir / 'Constitution of India.csv'
        if csv_path.exists():
            try:
                df_csv = pd.read_csv(csv_path).fillna('')
                part = []
                for _, row in df_csv.iterrows():
                    title = str(row.get('title', '')).strip()
                    if not title:
                        continue
                    section = f"Article {row.get('article', '')} - {title}"
                    part.append(_record('Constitution of India', section, str(row.get('description', ''))))
                records.extend(part)
                self.stdout.write(f'Imported {len(part)} from Constitution of India.csv')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'Could not parse Constitution CSV: {e}'))

        if output_csv.exists():
            try:
                existing = pd.read_csv(output_csv).fillna('')
                existing_records = existing[REQUIRED_COLUMNS].to_dict(orient='records')
                records = existing_records + records
                self.stdout.write(f'Loaded existing rows from {output_csv}: {len(existing_records)}')
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'Could not read existing CSV, continuing with imported only: {e}'))

        records = _dedupe_records(records)
        out_df = pd.DataFrame(records, columns=REQUIRED_COLUMNS).fillna('')
        out_df = out_df.sort_values(['law', 'section']).reset_index(drop=True)

        output_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)
        self.stdout.write(self.style.SUCCESS(f'Wrote {len(out_df)} merged rows to {output_csv}'))
