from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException
from fastapi.encoders import jsonable_encoder

from data import DummyDataBase
from models import Booking, BookingBaseModel, Tags

router = APIRouter()

db = DummyDataBase(model='bookings')
rooms_db = DummyDataBase(model='rooms')


@router.get('/', response_model=list[Booking], tags=[Tags.bookings])
def get_all_bookings():
    return db.retrieve_all()


@router.get('/{booking_id}', response_model=Booking, tags=[Tags.bookings])
def get_single_booking(booking_id: UUID):
    booking = db.retrieve(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail='Booking not found')
    return db.retrieve(booking_id)


@router.post('/', response_model=Booking, tags=[Tags.bookings])
def room_booking(booking_data: Annotated[BookingBaseModel, Form()]):
    room_id = booking_data.room_id
    room = rooms_db.retrieve(room_id)
    bookings = [row for row in db.retrieve_all() if row.get('room_id') == str(room_id)]

    # Validate room availability before booking
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if booking_data.is_room_available(bookings) is False:
        raise HTTPException(status_code=400, detail="Room is not available for selected date range")

    # Validate Start and End Date
    if booking_data.end_datetime <= booking_data.start_datetime:
        raise HTTPException(status_code=400, detail="End datetime shall be greater than Start datetime")

    # Calculate Total price of booking
    booking_data.nights = booking_data.calculate_nights()
    total_price = booking_data.nights * room.get('price_per_night')

    # Book a room and then mark as not available
    booked = db.create(**jsonable_encoder(booking_data), total_price=total_price)
    if booked is None:
        raise HTTPException(status_code=500, detail="Something Went Wrong while booking")

    # Deprecated - Room availability is decided based on current bookings
    # rooms_db.update(room_id, available=False)
    return booked


@router.delete('/{booking_id}', tags=[Tags.bookings])
def cancel_booking(booking_id: UUID):
    # Cancel booking and mark room as available
    booking = db.retrieve(booking_id)
    if not booking:
        raise HTTPException(status_code=400, detail='Booking not found')

    cancelled = db.delete(booking_id)
    if cancelled is False:
        raise HTTPException(status_code=500, detail='Something Went Wrong while cancelling booking')

    # Deprecated - Room availability is decided based on current bookings
    # rooms_db.update(booking.get('room_id'), available=True)
    return cancelled
