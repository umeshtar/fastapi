from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RoomBaseModel(BaseModel):
    model_config = {"extra": "forbid"}
    room_type: Literal['Single', 'Double', 'Suite']
    price_per_night: float = Field(gt=0)
    available: bool = False


class Room(RoomBaseModel):
    id: UUID


class BookingBaseModel(BaseModel):
    model_config = {"extra": "forbid"}
    room_id: UUID
    guest_name: str = Field(max_length=100)
    nights: int = Field(gt=0)


class Booking(BookingBaseModel):
    id: UUID
    total_price: float = Field(gt=0)
