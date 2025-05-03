from pydantic import BaseModel, Field
from datetime import datetime
from .conversation_outcome import ConversationOutcome
from ..public_user import PublicUser
from zoneinfo import ZoneInfo

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


def get_eastern_time():
    return datetime.now(ZoneInfo("America/New_York"))


class ConversationCreate(BaseModel):
    created_at: datetime = Field(default_factory=get_eastern_time)
    user_id: int
    chat_history: list[str]
    rating: int
    feedback: str
    outcome: ConversationOutcome


class Conversation(ConversationCreate):
    id: int
    user: PublicUser | None = None
