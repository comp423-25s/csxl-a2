from pydantic import BaseModel
from datetime import datetime
from .. import ConversationOutcome

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class Conversation(BaseModel):
    """Data for a chatbot conversation."""

    id: int
    created_at: datetime
    user_pid: str
    user_name: str
    chat_history: list[str]
    rating: int
    feedback: str
    outcome: ConversationOutcome
