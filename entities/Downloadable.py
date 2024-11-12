from pydantic import BaseModel, HttpUrl


class Downloadable(BaseModel):
    url: HttpUrl
    strategy: str
