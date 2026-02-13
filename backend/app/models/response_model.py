from pydantic import BaseModel
# from backend.app.schemas.user import Token
from typing import Any

class Response(BaseModel):
    data: Any