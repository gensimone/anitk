from enum import Enum


class _StrEnum(str, Enum):
    """ """


class Direction(_StrEnum):
    FORWARD = "forward"
    BACKWARD = "backward"


class SlideDirection(_StrEnum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class Axis(_StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Orientation(_StrEnum):
    CENTER = ""
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"
    NORTH_EAST = "ne"
    NORTH_WEST = "nw"
    SOUTH_EAST = "se"
    SOUTH_WEST = "sw"
