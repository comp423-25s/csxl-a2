"""Test data for the Conversation database with user relationships."""

import pytest
from sqlalchemy.orm import Session
from backend.models.conversations.conversation import Conversation, ConversationOutcome
from backend.entities.conversation_entity import ConversationEntity
from backend.entities.user_entity import UserEntity
from datetime import datetime, timedelta

from backend.test.services.reset_table_id_seq import reset_table_id_seq

from backend.test.services import user_data

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"

# Test users for the conversation feature
test_users = [
    user_data.student,
    user_data.instructor,
    user_data.ambassador,
    user_data.root,
]

# Sample conversations
conversation_one = Conversation(
    id=1,
    created_at=datetime.now() - timedelta(days=2),
    user_id=test_users[0].id,
    chat_history=[
        "User: I need to reserve a room",
        "Bot: What time do you need the room?",
        "User: Tomorrow at 2pm",
        "Bot: Room 123 is available, would you like to reserve it?",
        "User: Yes, please",
        "Bot: Room reserved successfully!",
    ],
    rating=5,
    feedback="This was very helpful!",
    outcome=ConversationOutcome.RESERVED_ROOM,
)

conversation_two = Conversation(
    id=2,
    created_at=datetime.now() - timedelta(days=1),
    user_id=test_users[1].id,
    chat_history=[
        "User: What are the coworking space hours today?",
        "Bot: The coworking space is open from 9am to 6pm today.",
        "User: Thanks!",
        "Bot: Is there anything else I can help you with?",
        "User: No, that's all",
        "Bot: Have a great day!",
    ],
    rating=4,
    feedback="It was okay.",
    outcome=ConversationOutcome.REQUESTED_INFORMATION,
)

conversation_three = Conversation(
    id=3,
    created_at=datetime.now() - timedelta(hours=5),
    user_id=test_users[2].id,
    chat_history=[
        "User: I need help with my assignment",
        "Bot: What course is the assignment for?",
        "User: COMP 423",
        "Bot: I can create an office hours ticket for you. Would you like that?",
        "User: Yes please",
        "Bot: Office hours ticket created. A TA will be with you shortly.",
    ],
    rating=5,
    feedback="This was very helpful!",
    outcome=ConversationOutcome.SUBMITTED_OH_TICKET,
)

new_conversation = Conversation(
    id=4,
    created_at=datetime.now(),
    user_id=test_users[3].id,
    chat_history=[
        "User: Can I cancel my reservation?",
        "Bot: Yes, what's the reservation time?",
        "User: Today at 3pm",
        "Bot: I found your reservation. Would you like to cancel it?",
        "User: Yes",
        "Bot: Your reservation has been cancelled.",
    ],
    rating=3,
    feedback="Could be improved.",
    outcome=ConversationOutcome.CANCELLED,
)

conversations = [conversation_one, conversation_two, conversation_three]


def insert_fake_data(session: Session):
    """Insert test conversations into the database"""

    # Make sure user entities exist first
    for user in test_users:
        # Check if user already exists
        existing_user = (
            session.query(UserEntity).filter(UserEntity.id == user.id).first()
        )
        if not existing_user:
            user_entity = UserEntity.from_model(user)
            session.add(user_entity)

    # Add conversations
    for conversation in conversations:
        entity = ConversationEntity.from_model(conversation)
        session.add(entity)

    # Reset ID sequence
    reset_table_id_seq(
        session,
        ConversationEntity,
        ConversationEntity.id,
        len(conversations) + 1,
    )

    session.commit()


@pytest.fixture(autouse=True)
def fake_data_fixture(session: Session):
    """Fixture to insert test conversation data"""
    insert_fake_data(session)
    session.commit()
    yield
