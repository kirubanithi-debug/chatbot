import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_PUNISHMENT = 'No direct penal punishment stated in this provision; follow statutory remedy/procedure.'
DEFAULT_NEXT_STEPS = (
    '1. Check the exact section text and latest amendments. '
    '2. File complaint/representation before the competent authority. '
    '3. Consult lawyer for case-specific legal remedy.'
)


def _pick_first(row: pd.Series, candidates: list[str]) -> str:
    for name in candidates:
        if name in row and str(row[name]).strip():
            return str(row[name]).strip()
    return ''


def _norm_text(value: str) -> str:
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def _build_law_label(act_name: str, section_no: str, section_title: str) -> str:
    act = _norm_text(act_name)
    sec = _norm_text(section_no)
    title = _norm_text(section_title)

    if sec and not sec.lower().startswith('section'):
        sec = f'Section {sec}'

    if act and sec:
        return f'{act} - {sec}'
    if act:
        return act
    return title or 'Central Law Provision'


def _build_section_label(section_no: str, section_title: str) -> str:
    sec = _norm_text(section_no)
    title = _norm_text(section_title)

    if sec and not sec.lower().startswith('section'):
        sec = f'Section {sec}'

    if sec and title:
        return f'{sec} - {title}'
    return sec or title or 'Provision details'


def _keywords(*parts: str) -> str:
    bag = ' '.join(_norm_text(p).lower() for p in parts if p)
    tokens = re.findall(r'[a-z0-9]+', bag)
    uniq = []
    seen = set()
    for token in tokens:
        if len(token) < 3:
            continue
        if token in seen:
            continue
        seen.add(token)
        uniq.append(token)
    return ' '.join(uniq)


def import_central_laws(input_path: Path, output_path: Path) -> None:
    src = pd.read_csv(input_path).fillna('')

    rows = []
    for _, row in src.iterrows():
        act_name = _pick_first(row, ['act_name', 'act', 'law', 'law_name'])
        section_no = _pick_first(row, ['section_no', 'section_number', 'section'])
        section_title = _pick_first(row, ['section_title', 'title', 'section_name'])
        punishment = _pick_first(row, ['punishment', 'penalty', 'sentence'])
        next_steps = _pick_first(row, ['next_steps'])

        law_label = _build_law_label(act_name=act_name, section_no=section_no, section_title=section_title)
        section_label = _build_section_label(section_no=section_no, section_title=section_title)

        if not law_label or not section_label:
            continue

        rows.append(
            {
                'law': law_label,
                'section': section_label,
                'punishment': _norm_text(punishment) or DEFAULT_PUNISHMENT,
                'next_steps': _norm_text(next_steps) or DEFAULT_NEXT_STEPS,
                'keywords': _keywords(act_name, section_no, section_title, punishment),
            }
        )

    imported = pd.DataFrame(rows, columns=['law', 'section', 'punishment', 'next_steps', 'keywords'])

    if output_path.exists():
        existing = pd.read_csv(output_path).fillna('')
    else:
        existing = pd.DataFrame(columns=['law', 'section', 'punishment', 'next_steps', 'keywords'])

    merged = pd.concat([existing, imported], ignore_index=True)
    merged = merged.drop_duplicates(subset=['law', 'section'], keep='first')
    merged.to_csv(output_path, index=False)

    print(f'Imported rows: {len(imported)}')
    print(f'Total rows after merge: {len(merged)}')
    print(f'Output: {output_path}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Import central laws into legal_sections.csv format.')
    parser.add_argument('--input', required=True, help='Path to source CSV file for central laws.')
    parser.add_argument(
        '--output',
        default=str(Path(__file__).resolve().parent.parent / 'data' / 'legal_sections.csv'),
        help='Path to output legal_sections.csv file.',
    )
    args = parser.parse_args()

    import_central_laws(input_path=Path(args.input), output_path=Path(args.output))


if __name__ == '__main__':
    main()
