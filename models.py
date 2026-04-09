from dataclasses import dataclass

@dataclass
class FileInfo:
    filepath: str
    filename: str
    rows: int | None = None
    cols: int | None = None

@dataclass
class Card:
    grid_pos: tuple[int, int]
    filepath: str
    bbox: tuple[int, int, int, int]
    quantidade: int = 0
    grid_shape: tuple[int, int] = (0, 0)


cardList: dict[int, Card] = {}
