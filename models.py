from uuid import UUID

from pydantic import BaseModel


class Room(BaseModel):
    id: UUID
    room_type: str
    price_per_night: float
    available: bool = False


class Booking(BaseModel):
    id: int
    room_id: int
    guest_name: str
    nights: int
    total_price: float
