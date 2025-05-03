"""Chat API

This API handles AI-powered chatbot requests using the OpenAI service.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
import json

from backend.models import User
from backend.models.chat import ChatRequest, ChatResponse
from backend.api.authentication import registered_user
from backend.models.coworking.reservation import ReservationPartial
from backend.services.office_hours.office_hours import OfficeHoursService
from backend.services.openai import OpenAIService
from backend.services.coworking.reservation import (
    ReservationService,
    ReservationException,
)
from backend.models.coworking import ReservationRequest, ReservationState
from backend.models.room import RoomPartial
from backend.services.office_hours.ticket import OfficeHourTicketService
from backend.models.office_hours.ticket import NewOfficeHoursTicket
from backend.services.office_hours.office_hours import OfficeHoursService
from backend.services.office_hours.ticket import OfficeHourTicketService
from backend.services.academics.course_site import CourseSiteService


api = APIRouter(prefix="/api", tags=["Chat"])
openapi_tags = {
    "name": "Chat",
    "description": "Natural language chatbot interface for room reservations.",
}


def get_user_course_sites(subject: User, course_site_svc: CourseSiteService):
    """
    Get all course sites associated with the current user.
    """
    return course_site_svc.get_user_course_sites(subject)


def get_office_hours_student_can_attend(
    subject: User, oh_event_svc: OfficeHoursService, site_id: int
):
    """
    Fetch office hours the student is allowed to attend for a course/site.
    """
    return oh_event_svc.get_office_hour_get_help_overview(subject, site_id)


def create_ticket(
    subject: User,
    oh_ticket_svc: OfficeHourTicketService,
    office_hours_id: int,
    description: str,
    ticket_type: str,
):
    ticket = NewOfficeHoursTicket(
        description=description, type=ticket_type, office_hours_id=office_hours_id
    )
    return oh_ticket_svc.create_ticket(subject, ticket)


def cancel_ticket(
    ticket_id: int, subject: User, oh_ticket_svc: OfficeHourTicketService
):
    return oh_ticket_svc.cancel_ticket(subject, ticket_id)


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
    oh_event_svc: OfficeHoursService = Depends(),
    course_site_svc: CourseSiteService = Depends(),
    oh_ticket_svc: OfficeHourTicketService = Depends(),
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
Today's time is {formatted}. 
If a user submits a message starting with "TA Ticket Submission", 
treat this as a completed request.Do not ask for more 
clarification. Call the submit_ticket function with the 
provided information. When calling submit_ticket, you
MUST use the correct office_hours_id shown in the most 
recent get_student_office_hours response. Do not use 0 
as a placeholder. If you do not know the correct 
office_hours_id, ask the user to select a session or 
call get_student_office_hours again.
If user requests do not 
have to do with booking study rooms or the CSXL, respond 
by suggesting what actions you can perform. When you respond,
convert the time into 12 hour time. When booking a 
room, you should only show times for after the current
time. Users can only book rooms if the start and end times 
fall exactly on the hour or half-hour, such as 1:00, 1:30, 2:00, etc. 
The total duration of a booking must not exceed 2 hours. They may
be exactly 2 hours. Do not allow bookings that start 
or end at times like 1:15 or 2:45, or any other 
time that does not end in :00 or :30. Only suggest and accept booking
times that meet these requirements, and reject or correct requests 
that do not follow the valid format.
When someone asks what time rooms are 
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
start date is before the end date. Use change_reservation
rather then update_reservation. If a user says update, change,
cancel, you should assume they mean the most recently shown
reservation unless otherwise specified. Do not say that the 
requested time exceeds the maximum booking time of two hours
if the user is requesting exactly two hours, book that time.
If the user says "cancel it",
or something similar you should assume they mean the most 
recently shown reservation unless otherwise specified.
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
            "name": "get_student_office_hours",
            "description": "Get the office hours for a specific course the student is taking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_code": {
                        "type": "string",
                        "description": "The course code and number, e.g., 'COMP 110'",
                    }
                },
                "required": ["course_code"],
            },
        },
        {
            "name": "submit_ticket",
            "description": "Submit a help request ticket for office hours",
            "parameters": {
                "type": "object",
                "properties": {
                    "office_hours_id": {"type": "integer"},
                    "description": {"type": "string"},
                    "ticket_type": {
                        "type": "integer",
                        "enum": [0, 1],
                        "enumDescriptions": [
                            "Conceptual help",
                            "Assignment help",
                        ],
                    },
                },
                "required": ["office_hours_id", "description", "ticket_type"],
            },
        },
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
        {
            "name": "get_user_reservations",
            "description": "Get a list of all current and upcoming reservations for the user",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "get_reservation",
            "description": "Get a reservation by its ID",
            "parameters": {
                "type": "object",
                "properties": {"reservation_id": {"type": "integer"}},
                "required": ["reservation_id"],
            },
        },
        {
            "name": "cancel_reservation",
            "description": "Cancel an existing reservation by its ID",
            "parameters": {
                "type": "object",
                "properties": {"reservation_id": {"type": "integer"}},
                "required": ["reservation_id"],
            },
        },
        {
            "name": "update_reservation",
            "description": "Change the start and end time of an existing reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "integer"},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                },
                "required": ["reservation_id", "start", "end"],
            },
        },
        {
            "name": "change_reservation",
            "description": "Change a reservation by canceling the original and reserving a new time",
            "parameters": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "integer"},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                },
                "required": ["reservation_id", "start", "end"],
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
                    "response": f"Room {reservation.room.id} reserved from {reservation.start.strftime('%I:%M%p')} to {reservation.end.strftime('%I:%M%p')}."
                }
            except ReservationException as e:
                return {"response": f"Reservation failed: {e}"}

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

        elif fn_name == "get_user_reservations":
            reservations = reservation_svc.get_current_reservations_for_user(
                subject, subject
            )
            if not reservations:
                return {"response": "You have no upcoming reservations."}

            formatted = "\n".join(
                f" ID: {r.id}, Room: {r.room.id if r.room else 'Unknown'}, "
                f"{r.start.strftime('%A %I:%M%p')} - {r.end.strftime('%I:%M%p')}"
                for r in reservations
            )

            return {"response": f"Here are your upcoming reservations:\n{formatted}"}

        elif fn_name == "get_reservation":
            try:
                reservation = reservation_svc.get_reservation(
                    subject, args["reservation_id"]
                )
                return {
                    "response": (
                        f"Reservation {reservation.id} is in room {reservation.room.id} "
                        f"from {reservation.start.strftime('%A %I:%M%p')} to {reservation.end.strftime('%I:%M%p')}."
                    )
                }
            except Exception as e:
                return {"response": f"Could not find reservation: {str(e)}"}

        elif fn_name == "cancel_reservation":
            try:
                reservation = reservation_svc.change_reservation(
                    subject,
                    ReservationPartial(
                        id=args["reservation_id"], state=ReservationState.CANCELLED
                    ),
                )
                return {
                    "response": f" Reservation {args['reservation_id']} has been cancelled."
                }
            except Exception as e:
                return {"response": f"Could not cancel reservation: {str(e)}"}

        elif fn_name == "update_reservation":
            try:
                reservation = reservation_svc.change_reservation(
                    subject,
                    ReservationPartial(
                        id=args["reservation_id"],
                        start=datetime.fromisoformat(args["start"]),
                        end=datetime.fromisoformat(args["end"]),
                    ),
                )
                return {
                    "response": f" Updated reservation {reservation.id} to {reservation.start.strftime('%I:%M%p')} - {reservation.end.strftime('%I:%M%p')}."
                }
            except Exception as e:
                return {"response": f"Could not update reservation: {str(e)}"}

        elif fn_name == "change_reservation":
            try:
                reservation_svc.change_reservation(
                    subject,
                    ReservationPartial(
                        id=args["reservation_id"],
                        state=ReservationState.CANCELLED,
                    ),
                )

                original = reservation_svc.get_reservation(
                    subject, args["reservation_id"]
                )

                new_request = ReservationRequest(
                    users=[subject],
                    room=RoomPartial(id=original.room.id),
                    start=datetime.fromisoformat(args["start"]),
                    end=datetime.fromisoformat(args["end"]),
                    state=ReservationState.DRAFT,
                )

                new_reservation = reservation_svc.draft_reservation(
                    subject, new_request
                )

                return {
                    "response": (
                        f" Reservation {args['reservation_id']} was cancelled.\n"
                        f" New reservation created for room {new_reservation.room.id} "
                        f"from {new_reservation.start.strftime('%I:%M%p')} to {new_reservation.end.strftime('%I:%M%p')}."
                    )
                }
            except Exception as e:
                print("Error changing reservation:", e)

                return {"response": f"Could not change reservation: {str(e)}"}

        elif fn_name == "get_student_office_hours":
            try:
                course_code = args["course_code"].strip().lower()

                term_overviews = get_user_course_sites(subject, course_site_svc)
                if not term_overviews:
                    return {"response": "No course sites found for your account."}

                now = datetime.now()

                current_terms = [
                    term for term in term_overviews if term.start <= now <= term.end
                ]
                matching_site_id = None
                for term in current_terms:
                    for site in term.sites:
                        full_code = f"{site.subject_code} {site.number}".lower()
                        if full_code == course_code:
                            matching_site_id = site.id
                            break
                    if matching_site_id:
                        break

                if not matching_site_id:
                    return {
                        "response": f"Could not find a course matching '{course_code}' in the current term."
                    }

                oh = oh_event_svc.get_office_hour_get_help_overview(
                    subject, matching_site_id
                )
                start_time = oh.event_start_time.strftime("%A, %B %d at %I:%M%p")
                end_time = oh.event_end_time.strftime("%A, %B %d at %I:%M%p")

                location = oh.event_location_description

                return {
                    "response": f"Your office hour for {course_code.upper()} is in {location} from {start_time} to {end_time}."
                }
            except Exception as e:
                return {"response": f"Failed to retrieve office hours: {e}"}

        elif fn_name == "submit_ticket":
            try:
                office_hours_id = args["office_hours_id"]
                description = args["description"]
                ticket_type = args["ticket_type"]

                ticket = NewOfficeHoursTicket(
                    description=description,
                    type=ticket_type,
                    office_hours_id=office_hours_id,
                )

                created_ticket = oh_ticket_svc.create_ticket(subject, ticket)

                ticket_type_str = "Conceptual" if ticket_type == 0 else "Assignment"
                return {
                    "response": (
                        f"Ticket created for {ticket_type_str} help.\n"
                        f"Your issue: {description}"
                    )
                }
            except Exception as e:
                return {"response": f"Failed to submit ticket: {e}"}

    print("GPT message:", response)
    print("GPT message content:", response.content)
    return {"response": response.content or "I'm not sure how to help with that."}
