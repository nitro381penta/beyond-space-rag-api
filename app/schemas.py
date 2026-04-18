from pydantic import BaseModel
from typing import List


class AskResponse(BaseModel):
    transcript: str
    display_text: str
    answer_text: str
    audio_base64: str


class RetrievedChunk(BaseModel):
    id: str
    source: str
    text: str
    distance: float