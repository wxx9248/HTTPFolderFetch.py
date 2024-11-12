from typing import List

from pydantic import BaseModel

from entities.File import File


class Folder(BaseModel):
    name: str
    folders: List["Folder"] = []
    files: List[File] = []


# Update forward references
Folder.model_rebuild()
