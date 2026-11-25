# ThesisMentor

Academic assistant for students: upload a thesis or paper (PDF), ask questions about it,
and get an answer that cites the pages it comes from.

## How it works

1. **Upload** (`POST /upload`): the PDF is saved, the text of every page is extracted with
   PyMuPDF (keeping the printed page numbers: i, ii, 1, 2…) and stored in `app/data/<doc_id>.json`.
2. **Search** (`POST /ask`): the backend ranks the pages against the question (BM25 keyword search)
   and returns the 4 most relevant ones.
3. **Answer**: the browser sends those pages and the question to an AI model through
   [Puter.js](https://docs.puter.com/) and shows the answer with clickable page sources.
   If the AI is unavailable, the relevant pages are still shown.

## Run locally (Windows)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/chat. The first question opens a Puter login window
(free account; each user's AI usage is billed to their own Puter account).

API documentation: http://127.0.0.1:8000/docs

## Tests

```powershell
pytest
```

## Project structure

```
app/
  main.py                      FastAPI app, static files
  api/endpoints/web.py         HTML pages (/ and /chat)
  api/endpoints/documents.py   POST /upload
  api/endpoints/chat.py        POST /ask
  infrastructure/pdf_processing.py   page text + page labels (PyMuPDF)
  infrastructure/registry.py   stores page indexes as JSON
  services/indexing_service.py builds the page index
  services/qa_service.py       ranks pages for a question
  schemas/chat.py              request/response models
  templates/, static/          frontend (HTML, CSS, JS)
tests/                         pytest tests + sample PDF
```

## Not done yet (ideas)

User accounts, several documents per project, bibliography export, semantic (vector) search.
