from pydantic import BaseModel, HttpUrl


class File(BaseModel):
    name: str
    url: HttpUrl
