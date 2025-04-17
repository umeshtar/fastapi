# Hotel Booking API

This is a simple Hotel Booking API built using FastAPI. It allows you to manage rooms and bookings. The API uses a file-based "database" (DummyDataBase) for data persistence.

## Features

* **Rooms:**
    * Create rooms with a type and price.
    * Retrieve all rooms, optionally filtered by room type.
    * Retrieve a single room by ID.
    * Update room information.
    * Delete a room.
* **Bookings:**
    * Create bookings for a room with a guest name, start date, and end date.
    * Retrieve all bookings.
    * Retrieve a single booking by ID.
    * Cancel a booking.
    * Automatically calculates the number of nights and total price for a booking.
    * Checks room availability based on existing bookings and specified date range.
* **Root:**
    * A simple "Hello World" endpoint for starting purpose

## Dependencies

* Python 3.10+
* FastAPI
* Pydantic

## Setup

1.  **Clone the repository:** https://github.com/umeshtar/fastapi.git

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install "fastapi[standard]"
    ```
    Pydantic is a dependency of FastAPI, so it will be installed automatically.

4.  **Run the application:**

    ```bash
    fastapi dev main.py
    ```

    This will start the FastAPI application with hot reloading, so any changes you make to the code will be automatically reflected.
    
6. **Testing:**

    ```bash
    http://127.0.0.1:8000/docs#/
    ```
    
   All endpoints and forms can be tested using auto generated FastAPI Swagger UI.
   
## API Endpoints

### Rooms

* `GET /rooms/`: Get all rooms.  Optional query parameter `room_type` to filter by type (e.g., `/rooms/?room_type=Single`).
* `GET /rooms/{room_id}`: Get a single room by ID.
* `POST /rooms/`: Create a new room.  Requires `room_type` (Single, Double, Suite) and `price_per_night` in the request.
* `PUT /rooms/{room_id}`: Update an existing room.  Requires `room_type` and `price_per_night` in the request.
* `DELETE /rooms/{room_id}`: Delete a room.

### Bookings

* `GET /bookings/`: Get all bookings.
* `GET /bookings/{booking_id}`: Get a single booking by ID.
* `POST /bookings/`: Create a new booking. Requires `room_id`, `guest_name`, `start_datetime`, and `end_datetime` in the request.  Use form data for the request.
* `DELETE /bookings/{booking_id}`: Cancel a booking.

### Root

* `GET /`:  Returns a simple "Hello World" message.

## Data Storage

The API uses a very basic file-based "database" implemented in `data.py`.  Data is stored in JSON files within the `database` directory.  This is *not* a production-ready database, but it's sufficient for simple testing.

## Error Logging

* Automatically captures and logs all uncaught exceptions.
* Stores error details like timestamp, message, and traceback.
* Returns a standardized JSON response with status code `500`.

## Models

The `models.py` file defines the data models used by the API:

* `Room`: Represents a room with its type, price, and availability.
* `Booking`: Represents a booking for a room, including the guest name, start and end dates, and total price.
* `RoomBaseModel`: Base model for creating/updating rooms.
* `BookingBaseModel`: Base model for creating bookings.
* `BookingDateTimeModel`:  A model to handle the start and end datetimes for bookings, including the logic to calculate the number of nights.
* `RoomType`: An enum for the possible room types (Single, Double, Suite).
* `Tags`: An enum for the tags used in the API documentation.

## Routes

The `routes` directory contains the route handlers for the API:

* `routes/rooms.py`: Defines the routes for managing rooms.
* `routes/bookings.py`: Defines the routes for managing bookings.
* `main.py`:  The main application file that creates the FastAPI app and includes the route handlers.

## Important Considerations

* **Dummy Database:** The `DummyDataBase` class is a very basic database implementation for demonstration purposes only.
* **Date Handling:** The `BookingDateTimeModel` in `models.py` contains the core logic for calculating the number of nights and checking room availability.  The docstrings explain the assumptions made about check-in/check-out times.
* **Error Handling:** The API uses FastAPI's `HTTPException` to handle errors, such as when a room or booking is not found, or when a room is not available for the requested dates. Unhandled exception are handled using global handler.
* **Form Data:** The booking creation endpoint (`POST /bookings/`) uses `Form(...)` to receive data.  This means you should send the data as form data, not as JSON.
* **Deprecation:** The `available` field in the `Room` model, and the `nights` field in the `BookingBaseModel` are deprecated. The availability of a room is now determined dynamically, and the number of nights is calculated within the `BookingDateTimeModel`.
