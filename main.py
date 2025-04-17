from fastapi import FastAPI

from handle_errors import register_global_error_handler
from models import Tags
from routes import rooms, bookings

# Create the FastAPI app instance
app = FastAPI()

# Register routers with prefixes for route grouping
app.include_router(rooms.router, prefix='/rooms')
app.include_router(bookings.router, prefix='/bookings')

# Register a global error handler for the entire app
register_global_error_handler(app)


# Basic welcome message
@app.get("/", tags=[Tags.root])
def read_root():
    return {"Hello": "World"}
