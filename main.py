from fastapi import FastAPI

from routes import rooms

app = FastAPI()

app.include_router(rooms.router, prefix='/room')


@app.get("/", tags=['root'])
def read_root():
    return {"Hello": "World"}
