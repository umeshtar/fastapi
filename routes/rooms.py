from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query, HTTPException
from fastapi.encoders import jsonable_encoder

from data import DummyDataBase
from models import Room, RoomBaseModel, RoomType, Tags

router = APIRouter()

db = DummyDataBase(model='rooms')


@router.get('/', response_model=list[Room], tags=[Tags.rooms])
def get_rooms(room_type: Annotated[RoomType | None, Query()] = None):
    rooms = db.retrieve_all()
    if room_type:
        rooms = [room for room in rooms if room.get('room_type') == room_type]
    return rooms


@router.get('/{room_id}', response_model=Room, tags=[Tags.rooms])
def get_single_room(room_id: UUID):
    room = db.retrieve(room_id)
    if room is None:
        raise HTTPException(status_code=400, detail='Room not found')
    return


@router.post('/', response_model=Room, tags=[Tags.rooms])
def create_room(room_data: Annotated[RoomBaseModel, Form()]):
    room = db.create(**jsonable_encoder(room_data))
    if not room:
        raise HTTPException(status_code=500, detail='Something went wrong while creating room')
    return room


@router.put('/{room_id}', response_model=Room, tags=[Tags.rooms])
def update_room(room_id: UUID, room_data: Annotated[RoomBaseModel, Form()]):
    room = db.retrieve(room_id)
    if room is None:
        raise HTTPException(status_code=400, detail='Room not found')

    room = db.update(room_id, **jsonable_encoder(room_data))
    if not room:
        raise HTTPException(status_code=500, detail='Something went wrong while updating room')
    return room


@router.delete('/{room_id}', tags=[Tags.rooms])
def delete_room(room_id: UUID):
    room = db.retrieve(room_id)
    if room is None:
        raise HTTPException(status_code=400, detail='Room not found')

    deleted = db.delete(room_id)
    if deleted is False:
        raise HTTPException(status_code=500, detail='Something Went Wrong while deleting room')
    return deleted
