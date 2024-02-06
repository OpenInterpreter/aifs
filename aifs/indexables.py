import os
from pathlib import Path
from typing import Optional

from . import settings


def is_indexable(path: str | Path):
    "Check If a path is indexable or not."
    p = Path(path)
    is_file = p.is_file()
    dir = p.parent if is_file else p

    if any(e in dir.parts for e in settings.DIRECTORIES_TO_IGNORE): 
        return False
    if not is_file:
        return True
    if p.name in settings.FILES_TO_IGNORE:
        return False
    if p.suffix in settings.EXTENSIONS_TO_IGNORE:
        return False
    return True

class PathEntity:
    """PathEntity class for representing a filesystem path."""
    
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).resolve()
        self.__pathstr = str(self.path)
        self.name = self.path.name
        if not self.path.exists():
            raise LookupError(f"{self.__pathstr!r} doesn't exists on the system.")

    def __eq__(self, other: 'PathEntity') -> bool:
        return self.path == other.path

    def __hash__(self) -> int:
        return hash(self.__pathstr)
    
    def __str__(self) -> str:
        return self.__pathstr

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__pathstr!r})"
    
    @property
    def base(self) -> str:
        if os.name == 'nt':
            return self.path.drive
        return str(list(self.path.parents)[-2])
    
class File(PathEntity):
    """Class for representing a path as a file."""
    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        if not self.path.is_file():
            raise LookupError(f"{self.__pathstr!r} if not a file.")
        
        self.directory = Directory(self.path.parent)
        """Parent of the file."""
        self.last_modified = self.path.lstat().st_mtime
        """Last modified time of the file."""


class Directory(PathEntity):
    """Class for representing a path as a directory."""
    def __init__(self, path: Optional[str | Path] = None) -> None:
        path =  path or Path.cwd()
        super().__init__(path)
        if not self.path.is_dir():
            raise NotADirectoryError(f"{self.__pathstr!r} is not a directory.")
    
    def __and__(self, key: str):
        """Concatenate and return as directory."""
        return Directory(self.path / key)

    def __or__(self, key: str):
        """Concatenate and return as file."""
        return File(self.path / key)

    @property
    def subdirectories(self) -> 'list[Directory]':
        """Subdirectories of the directory."""
        return [Directory(p) for p in self.path.rglob('*') if p.is_dir() and is_indexable(p)]

    @property
    def files(self) -> 'list[File]':
        """Files of the directory."""
        return [File(p) for p in self.path.rglob('*') if p.is_file() and is_indexable(p)]