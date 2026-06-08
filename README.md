# CODEDPipeline

Extract statistical tables from government PDF reports and export them as clean CSVs — with a web UI.

## Pipeline

```
PDF → Camelot (lattice) → Clean → Detect Headers → Build Columns → Validate → CSV + Catalog
```

- Handles bilingual Hindi-English PDFs (strips romanized Hindi artifacts)
- 184 / 186 tables extracted on sample DES report
- Exports per-table CSVs + `table_catalog.csv` metadata

## Stack

| Layer | Tech |
|---|---|
| PDF extraction | Camelot (lattice) |
| Cleaning | pandas + ftfy |
| API | FastAPI + uvicorn |
| Frontend | React + Vite |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── extract/          # Camelot PDF → DataFrame
│   │   ├── cleaning/         # Clean, detect headers, build columns
│   │   ├── standardization/  # Table names, metadata catalog
│   │   └── validation/       # Row/col minimum gate
│   ├── data/
│   │   ├── uploads/          # Uploaded PDFs (gitignored)
│   │   └── jobs/             # Per-job CSV outputs (gitignored)
│   └── tests/
└── frontend/                 # React + Vite UI
    └── src/
        ├── App.jsx
        └── App.css
```

## Setup

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install camelot-py ftfy pandas fastapi uvicorn python-multipart
```

### Frontend

```bash
cd frontend
npm install
```

## Run

**Backend** (from project root):
```bash
source venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --reload --port 8000
```

**Frontend** (in another terminal):
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`, upload a PDF, get CSVs.

## CLI (no UI)

```bash
PYTHONPATH=. python3 backend/tests/test_pipeline.py
```

Outputs to `backend/data/exports/`.

## Known Limitations

- No OCR — scanned (image-only) PDFs won't work
- Optimised for MP DES district statistical reports
- Multi-row merged headers partially reconstructed
