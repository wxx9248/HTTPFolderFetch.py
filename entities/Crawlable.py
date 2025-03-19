from pydantic import BaseModel, HttpUrl


class Crawlable(BaseModel):
    url: HttpUrl
    strategy: str
