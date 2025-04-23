"""Conversations API"""

from fastapi import APIRouter, Depends

from ..api.authentication import registered_user

from ..services.conversation import ConversationService

from ..models import User
from ..models.conversations.conversation import Conversation, ConversationCreate

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

api = APIRouter(prefix="/api/conversations")
openapi_tags = {
    "name": "Conversations",
    "description": "Create, update, and retrieve chatbot conversations.",
}


@api.post("", tags=["Conversations"], response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate,
    subject: User = Depends(registered_user),
    conversation_svc: ConversationService = Depends(),
) -> Conversation:
    return conversation_svc.create_conversation(conversation)


@api.get("/{conversation_id}", tags=["Conversations"])
def get_conversation(
    conversation_id: int,
    subject: User = Depends(registered_user),
    conversation_svc: ConversationService = Depends(),
) -> Conversation:
    """Get a conversation by ID."""
    return conversation_svc.get_conversation(conversation_id)


@api.put("/{conversation_id}/end", tags=["Conversations"])
def end_conversation(
    conversation_id: int,
    subject: User = Depends(registered_user),
    conversation_svc: ConversationService = Depends(),
):
    """End a conversation."""
    conversation_svc.end_conversation(conversation_id)


@api.get("/user/{user_id}", tags=["Conversations"])
def get_user_conversations(
    user_id: int,
    subject: User = Depends(registered_user),
    conversation_svc: ConversationService = Depends(),
) -> list[Conversation]:
    """Get all conversations for a specific user."""
    # Only admins or the user themselves should be able to see their conversations
    if subject.id != user_id:
        conversation_svc._permission_svc.enforce(
            subject, "conversation.list", f"conversation/{user_id}"
        )

    return conversation_svc.get_user_conversations(user_id)


@api.get("/me", tags=["Conversations"])
def get_my_conversations(
    subject: User = Depends(registered_user),
    conversation_svc: ConversationService = Depends(),
) -> list[Conversation]:
    """Get all conversations for the currently logged in user."""
    return conversation_svc.get_user_conversations(subject.id)
