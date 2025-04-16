from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form

from data import DummyDataBase
from models import Room, RoomBaseModel

router = APIRouter()

db = DummyDataBase(model='rooms')


@router.get('/', response_model=list[Room], tags=['Rooms'])
def get_rooms():
    return db.retrieve_all()


@router.get('/{room_id}', response_model=Room, tags=['Rooms'])
def get_single_room(room_id: UUID):
    return db.retrieve(room_id)


@router.post('/', response_model=Room, tags=['Rooms'])
def create_room(room_data: Annotated[RoomBaseModel, Form()]):
    return db.create(**room_data.model_dump())


@router.put('/{room_id}', response_model=Room, tags=['Rooms'])
def update_room(room_id: UUID, room_data: Annotated[RoomBaseModel, Form()]):
    return db.update(room_id, **room_data.model_dump())


@router.delete('/{room_id}', tags=['Rooms'])
def delete_room(room_id: UUID):
    return db.delete(room_id)
