from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, Session, SQLModel, create_engine, select


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


class Hero(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
    hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
    hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
    hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)

    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.add(hero_4)
        session.add(hero_5)
        session.add(hero_6)
        session.add(hero_7)

        session.commit()


def update_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero_1 = results.one()
        print("Hero 1:", hero_1)

        statement = select(Hero).where(Hero.name == "Captain North America")
        results = session.exec(statement)
        hero_2 = results.one()
        print("Hero 2:", hero_2)

        hero_1.age = 16
        hero_1.name = "Spider-Youngster"
        session.add(hero_1)

        hero_2.name = "Captain North America Except Canada"
        hero_2.age = 110
        session.add(hero_2)

        session.commit()
        session.refresh(hero_1)
        session.refresh(hero_2)

        print("Updated hero 1:", hero_1)
        print("Updated hero 2:", hero_2)


def delete_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.one()
        print("Hero: ", hero)

        session.delete(hero)
        session.commit()

        print("Deleted hero:", hero)

        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.first()

        if hero is None:
            print("There's no hero named Spider-Youngster")


def main():
    create_db_and_tables()
    create_heroes()
    update_heroes()
    delete_heroes()


if __name__ == "__main__":
    main()
