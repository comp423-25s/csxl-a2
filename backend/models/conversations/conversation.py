from pydantic import BaseModel
from datetime import datetime
from .conversation_outcome import ConversationOutcome
from ..public_user import PublicUser

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ConversationCreate(BaseModel):
    created_at: datetime
    user_id: int
    chat_history: list[str]
    rating: int
    feedback: str
    outcome: ConversationOutcome


class Conversation(ConversationCreate):
    id: int
    user: PublicUser | None = None
