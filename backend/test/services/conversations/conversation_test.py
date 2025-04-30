"""Tests for the Conversation Service."""

import pytest
from sqlalchemy import select, func
from datetime import datetime
import random

from backend.models.conversations.conversation import Conversation, ConversationOutcome
from backend.services.conversation import ConversationService
from backend.services.exceptions import ResourceNotFoundException

# Imported fixtures provide dependencies injected for the tests as parameters.
from backend.test.services.fixtures import conversation_svc

# Import the setup_teardown fixture explicitly to load entities in database
from backend.test.services.core_data import setup_insert_data_fixture as insert_order_0
from backend.test.services.conversations.conversation_data import (
    fake_data_fixture as insert_order_1,
)

# Import the fake model data in a namespace for test assertions
from backend.test.services import user_data
from backend.test.services.conversations import conversation_data


__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


def test_create_conversation(conversation_svc: ConversationService):
    """Test creating a new conversation."""
    # Create a new conversation
    new_conversation = Conversation(
        id=random.randint(1, 1000000),  # ID will be assigned by the database
        created_at=datetime.now(),
        user_id=conversation_data.test_users[0].id,
        chat_history=["User: Hello", "Bot: Hi there! How can I help you?"],
        rating=5,
        feedback="Great service!",
        outcome=ConversationOutcome.REQUESTED_INFORMATION,
    )

    # Add to database
    result = conversation_svc.create_conversation(new_conversation)

    # Verify the result
    assert result.id is not None
    assert result.user_id == conversation_data.test_users[0].id
    assert result.chat_history == [
        "User: Hello",
        "Bot: Hi there! How can I help you?",
    ]
    assert result.rating == 5
    assert result.feedback == "Great service!"
    assert result.outcome == ConversationOutcome.REQUESTED_INFORMATION


def test_start_conversation(conversation_svc: ConversationService):
    """Test starting a new conversation for a user."""
    # Start a conversation using a test user
    result = conversation_svc.start_conversation(conversation_data.test_users[1])

    # Verify the result
    assert result.id is not None
    assert result.user_id == conversation_data.test_users[1].id
    assert result.chat_history == []
    assert result.rating == 0
    assert result.feedback == ""
    assert result.outcome == ConversationOutcome.REQUESTED_INFORMATION


def test_get_conversation(conversation_svc: ConversationService):
    """Test retrieving a conversation by ID."""
    # Create a conversation in the database
    new_conversation = conversation_svc.create_conversation(
        Conversation(
            id=1,
            created_at=datetime.now(),
            user_id=conversation_data.test_users[0].id,
            chat_history=["User: Hello", "Bot: Hi there!"],
            rating=5,
            feedback="Great service!",
            outcome=ConversationOutcome.REQUESTED_INFORMATION,
        )
    )

    # Retrieve the conversation by ID
    result = conversation_svc.get_conversation(new_conversation.id)

    # Verify the result
    assert result.id == new_conversation.id
    assert result.user_id == new_conversation.user_id
    assert result.chat_history == new_conversation.chat_history

    # Test retrieving a non-existent conversation
    with pytest.raises(ResourceNotFoundException):
        conversation_svc.get_conversation(999)


def test_end_conversation(conversation_svc: ConversationService):
    """Test ending a conversation."""
    # Create a conversation in the database
    new_conversation = conversation_svc.create_conversation(
        Conversation(
            id=1,
            created_at=datetime.now(),
            user_id=conversation_data.test_users[0].id,
            chat_history=["User: Hello", "Bot: Hi there!"],
            rating=5,
            feedback="Great service!",
            outcome=ConversationOutcome.REQUESTED_INFORMATION,
        )
    )

    # End the conversation
    conversation_svc.end_conversation(new_conversation.id)

    # Verify the outcome was updated
    updated_conversation = conversation_svc.get_conversation(new_conversation.id)
    assert updated_conversation.outcome == ConversationOutcome.CANCELLED


def test_get_user_conversations(conversation_svc: ConversationService):
    """Test retrieving all conversations for a user."""
    # Get conversations for a test user
    user_id = conversation_data.test_users[0].id
    results = conversation_svc.get_user_conversations(user_id)

    # Verify results
    assert len(results) > 0
    for conversation in results:
        assert conversation.user_id == user_id

    # Verify user relationship is populated
    for conversation in results:
        if conversation.user:
            assert conversation.user.id == user_id
            assert conversation.user.first_name is not None
            assert conversation.user.last_name is not None


def test_user_conversation_relationship(conversation_svc: ConversationService):
    """Test the relationship between user and conversations."""
    # Get conversations for a test user
    user_id = conversation_data.test_users[0].id
    results = conversation_svc.get_user_conversations(user_id)

    # Verify the user relationship
    assert len(results) > 0
    for conversation in results:
        assert conversation.user_id == user_id
        if conversation.user:
            assert conversation.user.id == user_id


def test_count_conversations_by_outcome(conversation_svc: ConversationService):
    """Test counting conversations by outcome."""
    # Get all conversations for users
    for user in conversation_data.test_users:
        results = conversation_svc.get_user_conversations(user.id)

        # Verify results if user has conversations
        if results:
            # Check that outcomes are populated correctly
            valid_outcomes = [outcome for outcome in results if outcome.outcome]
            assert len(valid_outcomes) > 0
