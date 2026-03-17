# Import 893 Central Laws into this Project

## Why this step is needed
The project can store laws as:
- law
- section
- punishment
- next_steps
- keywords

To insert all 893 central laws correctly, use an official/reliable source CSV and import it.

## 1) Prepare source CSV
Create a CSV with these columns (minimum):
- `act_name`
- `section_no`
- `section_title`
- `punishment` (if available)
- `next_steps` (optional)

You can start from:
- `backend/data/central_laws_template.csv`

## 2) Run importer
From `backend/`:

```bash
/home/kiruba/chatbot/.venv/bin/python scripts/import_central_laws.py --input data/your_central_laws.csv
```

This merges into:
- `backend/data/legal_sections.csv`

## 3) Rebuild vector store

```bash
/home/kiruba/chatbot/.venv/bin/python chat/rag_setup.py
```

## Notes
- Not every central law section has a criminal punishment; many are procedural/civil.
- For such rows, importer sets fallback punishment text.
- Always verify legal text and amendments before production use.
