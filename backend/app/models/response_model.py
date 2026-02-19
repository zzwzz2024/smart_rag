from pydantic import BaseModel
from typing import Any

class Response(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Any = None