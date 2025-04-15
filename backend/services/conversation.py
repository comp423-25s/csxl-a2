"""
The Conversation Service allows the API to add chatbot conversations to the database.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.conversations.conversation import Conversation
from backend.models.conversations.conversation_outcome import ConversationOutcome
from backend.models.user import User


from ..database import db_session
from .exceptions import ResourceNotFoundException

from ..services.permission import PermissionService
from ..services.coworking import PolicyService, OperatingHoursService

from ..entities import ConversationEntity, UserEntity


__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ConversationService:
    """Service that performs all of the actions on the `conversation` table"""

    def __init__(
        self,
        session: Session = Depends(db_session),
        permission_svc: PermissionService = Depends(),
        policies_svc: PolicyService = Depends(),
        operating_hours_svc: OperatingHoursService = Depends(),
    ):
        """Initializes the session"""
        self._session = session
        self._permission_svc = permission_svc
        self._policies_svc = policies_svc
        self._operating_hours_svc = operating_hours_svc

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """Creates a new conversation record in the database."""
        entity = ConversationEntity.from_model(conversation)
        self._session.add(entity)
        self._session.commit()
        return entity.to_model()

    def start_conversation(self, user: User) -> Conversation:
        """Starts a new conversation for the user."""
        conversation_entity = ConversationEntity(
            created_at=datetime.now(),
            user_id=user.id,
            chat_history=[],
            rating=0,
            feedback="",
            outcome=ConversationOutcome.REQUESTED_INFORMATION,
        )
        self._session.add(conversation_entity)
        self._session.commit()
        return conversation_entity.to_model()

    def end_conversation(self, conversation_id: int) -> None:
        """Ends a conversation by marking it as finished."""
        conversation = self._session.get(ConversationEntity, conversation_id)
        if not conversation:
            raise ResourceNotFoundException("Conversation not found")

        # We don't have an end_time field, so we'll just update the outcome
        conversation.outcome = ConversationOutcome.CANCELLED
        self._session.commit()

    def get_conversation(self, conversation_id: int) -> Conversation:
        """Retrieves a conversation by its ID."""
        conversation = self._session.get(ConversationEntity, conversation_id)
        if not conversation:
            raise ResourceNotFoundException("Conversation not found")

        return conversation.to_model()

    def get_user_conversations(self, user_id: int) -> list[Conversation]:
        """Retrieves all conversations for a specific user."""
        from sqlalchemy import select

        query = select(ConversationEntity).where(ConversationEntity.user_id == user_id)
        conversations = self._session.scalars(query).all()

        return [conversation.to_model() for conversation in conversations]
