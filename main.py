import time
from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from configs import Settings
from handle_errors import register_global_error_handler
from models import Tags
from routes import rooms, bookings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Application Started', time.perf_counter())
    yield
    print('Application Stopped', time.perf_counter())


# Create the FastAPI app instance
app = FastAPI(lifespan=lifespan)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers with prefixes for route grouping
app.include_router(rooms.router, prefix='/rooms')
app.include_router(bookings.router, prefix='/bookings')

# Register a global error handler for the entire app
register_global_error_handler(app)


# Basic welcome message
@app.get("/", tags=[Tags.root])
def read_root():
    return {"Hello": "World"}


templates = Jinja2Templates(directory="templates")


@app.get('/home/{pk}', response_class=HTMLResponse)
def read_template(request: Request, pk: str):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": pk}
    )


@app.get('/chat', response_class=HTMLResponse)
def read_template(request: Request):
    return templates.TemplateResponse(
        request=request, name="chat.html"
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print("I am called", data)
        await websocket.send_text(f"Message: {data}")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        for connection in self.active_connections:
            if not connection == websocket:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", websocket)


@lru_cache
def get_settings():
    return Settings()


@app.get("/env_data")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
    }
