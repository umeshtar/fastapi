from fastapi import FastAPI

from models import Tags
from routes import rooms, bookings

app = FastAPI()

app.include_router(rooms.router, prefix='/rooms')
app.include_router(bookings.router, prefix='/bookings')


@app.get("/", tags=[Tags.root])
def read_root():
    return {"Hello": "World"}
