"""Enum for the state a chatbot conversation can end in."""

from enum import Enum

__authors__ = ["Ryan Krasinski"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ConversationOutcome(Enum):
    """
    Enum for the outcome of a chatbot conversation.
    """

    RESERVED_ROOM = "Reserved Room"
    REQUESTED_INFORMATION = "Requested Information"
    SUBMITTED_OH_TICKET = "Submitted OH Ticket"
    CANCELLED = "Cancelled Request"
