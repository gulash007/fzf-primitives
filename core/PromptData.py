from pathlib import Path
from pydantic import BaseModel

STORAGE_PATH = Path("experimental/.tempstorage/temp.json")


class PromptData(BaseModel):
    """A prompt should be reproducible with this data. Basically any program (and therefore fzf) should
    be able to deserialize it and access it"""
