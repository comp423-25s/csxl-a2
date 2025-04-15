"""Definition of SQLAlchemy table-backed object mapping entity for chatbot conversations."""

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .entity_base import EntityBase
from typing import Self
from ..models.conversations.conversation import Conversation, ConversationOutcome
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB

__authors__ = ["Ryan Krasinski", "Luke Allen"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ConversationEntity(EntityBase):
    """Serves as the database model schema defining the shape of the `Conversation` table"""

    __tablename__ = "conversation"

    # ID of the conversation
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Time when the conversation was created
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # ID of the user who started the conversation
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    # Relationship to the user
    user: Mapped["UserEntity"] = relationship(back_populates="conversations")
    # Conversation history between the user and the chatbot
    chat_history: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    # 'Star' rating of the conversation
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    # Written feedback of the conversation
    feedback: Mapped[str] = mapped_column(String, nullable=False)
    # Outcome of the conversation (e.g. 'reserved room', 'requested information', 'submitted OH ticket')
    outcome: Mapped[ConversationOutcome] = mapped_column(
        SQLAlchemyEnum(ConversationOutcome), nullable=False
    )

    @classmethod
    def from_model(cls, model: Conversation) -> Self:
        """Converts a 'Conversation' model to a 'ConversationEntity'

        Parameters:
            - model (Conversation): The model to convert to an entity
        Returns:
            ConversationEntity: The converted entity
        """
        return cls(
            id=model.id,
            created_at=model.created_at,
            user_id=model.user_id,
            chat_history=model.chat_history,
            rating=model.rating,
            feedback=model.feedback,
            outcome=model.outcome,
        )

    def to_model(self) -> Conversation:
        """Converts the 'ConversationEntity' to a 'Conversation' model

        Returns:
            Conversation: The converted model
        """
        return Conversation(
            id=self.id,
            created_at=self.created_at,
            user_id=self.user_id,
            user=self.user.to_public_model() if self.user else None,
            chat_history=self.chat_history,
            rating=self.rating,
            feedback=self.feedback,
            outcome=self.outcome,
        )
