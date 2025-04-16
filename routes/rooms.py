from typing import Annotated

from fastapi import APIRouter, Body

from data import DummyDataBase
from models import Room

router = APIRouter()

db = DummyDataBase(model='rooms')


@router.get('/', tags=['Rooms'])
def get_rooms():
    return db.retrieve_all()


@router.post('/', response_model=Room, tags=['Rooms'])
def create_room(room_data: Annotated[Room, Body()]):
    return db.create(**room_data.model_dump())
