"""Chat API

This API handles AI-powered chatbot requests using the OpenAI service.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import json

from backend.models import User
from backend.models.chat import ChatRequest, ChatResponse
from backend.api.authentication import registered_user
from backend.services.openai import OpenAIService
from backend.services.coworking.reservation import (
    ReservationService,
    ReservationException,
)
from backend.models.coworking import ReservationRequest, ReservationState
from backend.models.room import RoomPartial

api = APIRouter(prefix="/api", tags=["Chat"])
openapi_tags = {
    "name": "Chat",
    "description": "Natural language chatbot interface for room reservations.",
}


@api.post("/chat", response_model=ChatResponse)
def chat_with_bot(
    request: ChatRequest,
    openai_svc: OpenAIService = Depends(),
    reservation_svc: ReservationService = Depends(),
    subject: User = Depends(registered_user),
):
    print("Chat endpoint hit")
    print("Incoming ChatRequest message:", request.message)
    print("Incoming ChatRequest history:", request.history)

    today = datetime.now().strftime("%A, %B %d, %Y")

    messages = [
        {
            "role": "system",
            "content": f"""
You are a helpful assistant for booking study rooms.
Today's date is {today}. When you respond with a date, 
format it in plain English with the day of the week. 
You only book study rooms that are listed. If you get 
a room that is lowercase you should change it to uppercase. 
You only book rooms if the time is available. You only book 
rooms with the start time before the end time. Give helpful 
advice for times to book if not listed. If a student requests
a room provide the next available time and ask if they want to book it.
If a student requests a time that is not available, provide the next available time.
If a student requests a room that is not available, provide the next available room.
""",
        }
    ]

    if request.history:
        messages.extend([msg.model_dump() for msg in request.history])

    messages.append({"role": "user", "content": request.message})

    functions = [
        {
            "name": "get_available_rooms",
            "description": "Check available rooms on a specific date",
            "parameters": {
                "type": "object",
                "properties": {"date": {"type": "string", "format": "date"}},
                "required": ["date"],
            },
        },
        {
            "name": "reserve_room",
            "description": "Reserve a room for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_id": {"type": "string"},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                },
                "required": ["room_id", "start", "end"],
            },
        },
    ]

    response = openai_svc.interpret_with_functions(
        messages=messages,
        functions=functions,
    )

    if response.function_call:
        fn = response.function_call
        fn_name = fn.name
        args = json.loads(fn.arguments)

        if fn_name == "get_available_rooms":
            date = datetime.fromisoformat(args["date"])
            availability = reservation_svc.get_map_reserved_times_by_date(date, subject)
            available_rooms = [
                room_id
                for room_id, timeslots in availability.reserved_date_map.items()
                if any(slot == 0 for slot in timeslots)
            ]
            if available_rooms:
                pretty_date = date.strftime("%A, %B %d")
                return {
                    "response": f"Available rooms on {pretty_date}: {', '.join(available_rooms)}"
                }
            else:
                return {"response": f"Sorry, no rooms are available on {args['date']}"}

        elif fn_name == "reserve_room":
            try:
                start = datetime.fromisoformat(args["start"])
                end = datetime.fromisoformat(args["end"])
                request_model = ReservationRequest(
                    users=[subject],
                    room=RoomPartial(id=args["room_id"]),
                    start=start,
                    end=end,
                    seats=[],
                    state=ReservationState.DRAFT,
                )
                reservation = reservation_svc.draft_reservation(subject, request_model)
                return {
                    "response": f"✅ Room {reservation.room.id} reserved from {reservation.start.strftime('%I:%M%p')} to {reservation.end.strftime('%I:%M%p')}."
                }
            except ReservationException as e:
                return {"response": f"❌ Reservation failed: {e}"}

    print("GPT message:", response)
    print("GPT message content:", response.content)
    return {"response": response.content or "I'm not sure how to help with that."}
