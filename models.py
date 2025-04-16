from uuid import UUID

from pydantic import BaseModel, Field


class Room(BaseModel):
    id: UUID
    room_type: str
    price_per_night: float = Field(le=100, gt=0)
    available: bool = False


class Booking(BaseModel):
    id: int
    room_id: int
    guest_name: str
    nights: int
    total_price: float
