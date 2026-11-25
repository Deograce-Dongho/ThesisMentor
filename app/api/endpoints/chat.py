from fastapi import APIRouter, HTTPException

from app.infrastructure.registry import load_index
from app.schemas.chat import AskRequest, AskResponse
from app.services.qa_service import search_pages

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """Return the pages of the document most relevant to the question.
    The browser then sends them to the AI (Puter.js) to write the answer."""
    pages = load_index(req.doc_id)
    if pages is None:
        raise HTTPException(status_code=404, detail="Document not found. Please upload it again.")
    return AskResponse(doc_id=req.doc_id, query=req.query, sources=search_pages(pages, req.query))
