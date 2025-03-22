from enum import Enum


class UIMode(Enum):
    """Modes that the UI can be in. The UI can be in at most one mode at any given time."""

    NORMAL = 0
    PLACE_MOTIF = 1
    REMOVE_MOTIF = 2
    LASSO_SELECTION = 3
    WAND_SELECTION = 4
    PAINT_SELECTION = 5
    RECT_SELECTION = 6
