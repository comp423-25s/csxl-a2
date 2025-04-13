"""Chat API

This API handles AI-powered chatbot requests using the OpenAI service.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
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


def get_available_time_ranges(time_slots: list[int], start_time: datetime) -> list[str]:
    ranges = []
    slot_duration = timedelta(minutes=30)
    current_start = None

    for i, slot in enumerate(time_slots):
        if slot == 0:
            if current_start is None:
                current_start = start_time + i * slot_duration
        else:
            if current_start is not None:
                current_end = start_time + i * slot_duration
                start_str = current_start.strftime("%I:%M%p").lstrip("0")
                end_str = current_end.strftime("%I:%M%p").lstrip("0")
                ranges.append(f"{start_str} - {end_str}")
                current_start = None

    if current_start is not None:
        current_end = start_time + len(time_slots) * slot_duration
        start_str = current_start.strftime("%I:%M%p").lstrip("0")
        end_str = current_end.strftime("%I:%M%p").lstrip("0")
        ranges.append(f"{start_str} - {end_str}")
    return ranges


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
    time = datetime.now()
    formatted = time.strftime("%H:%M:%S")

    messages = [
        {
            "role": "system",
            "content": f"""
You are a helpful assistant for booking study rooms.
Today's date is {today}. When you respond with a date, 
format it in plain English with the day of the week.
Today's time is {formatted}. When you respond,
convert the time into 12 hour time. When booking a 
room, you should only show times for after the current
time. You should only try and book rooms for after the 
current time. When someone asks what time rooms are 
available provide the hour times not the day times.
Rooms are available to be booked in thirty
minute increments for any amount less than or equal to
two hours. Ensure you find the length of time being 
requested and if it is exactly two hours or shorter 
and available book it. If you can not book the full time 
requested ask if they want to book for a shorter amount 
of time rather than booking a random time. You can 
reserve rooms for days other than today. If they say a
day of the week, convert it into the nearest day that
day of the week falls on. Only search for rooms where the
start date is before the end date.
They can be booked over multiple hours including between 
hours. You can book a room for two consecutive hours.
You only book study rooms that are listed. If a student
requests to reserve a room but does not provide a 
specific room or time, list all available hours. Use the 
message history to decide if a student is asking for 
available rooms for the day or available hour times for 
a room. If you get a room that is lowercase you should 
change it to uppercase. You only book rooms if the time 
is available. You only book rooms with the start time 
before the end time. Give helpful advice for times to 
book if not listed. If a student requests a room provide
the next available hour times and ask if they want to 
book it. If a student requests a time that is not 
available, provide the next available time. If a student 
requests a room that is not available, provide the next 
available room.
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
        {
            "name": "get_room_availability",
            "description": "Get the available hours for a specific room on a given date",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_id": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["room_id", "date"],
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
            return {
                "response": (
                    f"Available rooms on {date.strftime('%A, %B %d')}: "
                    f"{', '.join(available_rooms) if available_rooms else 'None'}"
                )
            }

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

        elif fn_name == "get_room_availability":
            date = datetime.fromisoformat(args["date"])
            room_id = args["room_id"].upper()

            availability = reservation_svc.get_map_reserved_times_by_date(date, subject)
            room_timeslots = availability.reserved_date_map.get(room_id)

            if room_timeslots is None:
                return {"response": f"Room {room_id} not found."}

            ranges = get_available_time_ranges(
                room_timeslots, availability.operating_hours_start
            )

            return {
                "response": (
                    f"Available times for {room_id} on {date.strftime('%A, %B %d')}: "
                    f"{', '.join(ranges) if ranges else 'None'}"
                )
            }

    print("GPT message:", response)
    print("GPT message content:", response.content)
    return {"response": response.content or "I'm not sure how to help with that."}
