from fastapi import APIRouter, Depends, HTTPException
from backend.services.room import RoomService
from backend.models.user import User
from backend.api.authentication import registered_user

router = APIRouter()


@router.patch("/rooms/{room_id}/toggle-availability")
def toggle_room_availability(
    room_id: str,
    room_service: RoomService = Depends(),
    subject: User = Depends(registered_user),
):
    try:
        room = room_service.toggle_availability(subject, room_id)
        return {"id": room.id, "is_available": room.is_available}
    except HTTPException as e:
        raise e
