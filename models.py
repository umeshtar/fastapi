from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, SQLModel, create_engine, Relationship


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


# class Hero(SQLModel, table=True):
#     id: int | None = SQLField(default=None, primary_key=True)
#     name: str = SQLField(index=True)
#     secret_name: str
#     age: int | None = SQLField(default=None, index=True)

class TeamBase(SQLModel):
    name: str = SQLField(index=True)
    headquarters: str


class Team(TeamBase, table=True):
    id: int | None = SQLField(default=None, primary_key=True)

    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: int


class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None


class HeroBase(SQLModel):
    name: str = SQLField(index=True)
    secret_name: str
    age: int | None = SQLField(default=None, index=True)

    team_id: int | None = SQLField(default=None, foreign_key="team.id")


class Hero(HeroBase, table=True):
    id: int | None = SQLField(default=None, primary_key=True)

    team: Team | None = Relationship(back_populates="heroes")


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    pass


class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None


class HeroPublicWithTeam(HeroPublic):
    team: TeamPublic | None = None


class TeamPublicWithHero(TeamPublic):
    heroes: list[HeroPublic] = []


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
