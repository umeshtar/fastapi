import os
import traceback
from datetime import datetime

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse


def register_global_error_handler(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        try:
            with open(os.path.join(f"errors.txt"), 'a') as f:
                f.write(
                    f"Time: {datetime.now()}\n"
                    f"Error Message: {exc}\n"
                    f"Error Traceback: {traceback.format_exc()}\n\n"
                )
        except Exception as e:
            print(f"Error while logging errors: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
