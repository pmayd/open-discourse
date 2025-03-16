from pathlib import Path
from typing import Callable, List

from pydantic import BaseModel


class DoitTaskConfig(BaseModel):
    name: str
    actions: List[Callable | str]
    targets: List[str | Path]
    task_dep: List[str] | None = []
    file_dep: List[str | Path] | None = []
    uptodate: List[Callable] | None = []
