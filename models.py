from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from data import DummyDataBase


class Tags(str, Enum):
    rooms = 'Rooms'
    bookings = 'Bookings'
    root = 'Root'


class RoomType(str, Enum):
    SINGLE = 'Single'
    DOUBLE = 'Double'
    SUITE = 'Suite'


class RoomBaseModel(BaseModel):
    model_config = {"extra": "forbid"}
    room_type: RoomType
    price_per_night: float = Field(gt=0)
    available: bool = Field(default=False, deprecated=True)  # Availability is calculated based on start and end time of booking


class Room(RoomBaseModel):
    id: UUID


class BookingDateTimeModel(BaseModel):
    """
        Assumptions:
            Checkin checkout timings are assumed 12:00 to 12:00 for charging per night
            Rooms will be available for other customer as per actual checkout of old customer not the 12:00 to 12:00
            Example:
                1. Customer 1 stay for 13:00 to 20:00 - Charged 1 night pay
                2. Customer 2 stay for 22:00 to 11:00 - Charged 1 night pay
                for 24-hour cycle hotel is flexible to earn multiple nights pay
    """
    start_datetime: datetime
    end_datetime: datetime

    def calculate_nights(self):
        """
            Calculate number_of_nights of 12:00-to-12:00 periods
            between start_datetime and end_datetime to charge customer.
        """
        count = 0
        current = self.start_datetime.replace(hour=12, minute=0, second=0, microsecond=0)

        if self.start_datetime < current:
            current -= timedelta(days=1)

        while current < self.end_datetime:
            count += 1
            current += timedelta(days=1)

        return count

    def is_room_available(self, bookings):
        """
            Check if room is available between start_date and end_date.
            `existing_bookings` should be a list of BookingBaseModel or dicts with start/end dates.
        """
        for data in bookings:
            booking = BookingDateTimeModel(**data)
            if not (self.end_datetime <= booking.start_datetime or self.start_datetime >= booking.end_datetime):
                return False  # Overlapping booking found
        return True


class BookingBaseModel(BookingDateTimeModel):
    model_config = {"extra": "forbid"}
    room_id: UUID
    guest_name: str = Field(max_length=100)
    nights: int = Field(gt=0, deprecated=True)  # Nights are calculated based on start and end time of booking


class Booking(BookingBaseModel):
    id: UUID
    total_price: float = Field(gt=0)
