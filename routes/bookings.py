from http.client import HTTPException
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form

from data import DummyDataBase
from models import Booking, BookingBaseModel, Room

router = APIRouter()

db = DummyDataBase(model='bookings')
rooms_db = DummyDataBase(model='rooms')


@router.get('/', response_model=list[Booking], tags=['Bookings'])
def get_all_bookings():
    return db.retrieve_all()


@router.get('/{booking_id}', response_model=Booking, tags=['Bookings'])
def get_single_booking(booking_id: UUID):
    return db.retrieve(booking_id)


@router.post('/', response_model=Booking, tags=['Bookings'])
def room_booking(booking_data: Annotated[BookingBaseModel, Form()]):
    # Validate room availability before booking
    room_id = booking_data.room_id
    room = rooms_db.retrieve(room_id)
    if room is None:
        raise HTTPException("Room not found")
    if room.get('available') is False:
        raise HTTPException("Room already booked")

    # Calculate Total price of booking
    total_price = booking_data.nights * room.get('price_per_night')

    # Book a room and then mark as not available
    booked = db.create(
        **{**booking_data.model_dump(), 'room_id': str(room_id)},
        total_price=total_price
    )
    if booked is None:
        raise HTTPException("Something Went Wrong while booking")
    rooms_db.update(room_id, available=False)
    return booked


@router.delete('/{booking_id}', tags=['Bookings'])
def cancel_booking(booking_id: UUID):
    # Cancel booking and mark room as available
    booking = db.retrieve(booking_id)
    cancelled = db.delete(booking_id)
    if cancelled is False:
        raise HTTPException('Something went wrong while cancelling booking')

    rooms_db.update(booking.get('room_id'), available=True)
    return cancelled
