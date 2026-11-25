from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    doc_id: str
    query: str = Field(min_length=1, max_length=1000)


class PageHit(BaseModel):
    page_index: int  # 0-based index, for the PDF viewer (#page = page_index + 1)
    label: str       # page number printed in the document (i, ii, 1, 2…)
    score: float
    snippet: str     # short extract to display
    text: str        # longer text passed to the AI as context


class AskResponse(BaseModel):
    doc_id: str
    query: str
    sources: list[PageHit]
