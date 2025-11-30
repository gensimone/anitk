import logging
from actkinter.base import BaseFrame, Direction, Request
from actkinter.enums import SlideDirection


logger = logging.getLogger(__name__)


class SlideFrame(BaseFrame):
    def __init__(
        self,
        xstart: float,
        ystart: float,
        xend: float,
        yend: float,

        slide_direction: SlideDirection,
        disappear: bool = False,
        automatic_scaling: bool = False,

        forward_offset: float = 0.001,
        backward_offset: float = 0.001,

        forward_speed: int = 10,
        backward_speed: int = 10,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.disappear = disappear
        self.automatic_scaling = automatic_scaling
        self.slide_direction = slide_direction

        self.forward_offset = forward_offset
        self.backward_offset = backward_offset

        self.forward_speed = forward_speed
        self.backward_speed = backward_speed

        self.xstart = xstart
        self.ystart = ystart

        self.xend = xend
        self.yend = yend

        if self._opened is True:
            self._xactual = xstart
            self._yactual = ystart
        else:
            self._xactual = xend
            self._yactual = yend

        self._place(self._xactual, self._yactual)

    @property
    def xend(self) -> float:
        return self._xend

    @xend.setter
    def xend(self, value: float) -> None:
        self._xend = self._get_coordinate(value, "xend")

    @property
    def yend(self) -> float:
        return self._yend

    @yend.setter
    def yend(self, value: float) -> None:
        self._yend = self._get_coordinate(value, "yend")

    def _get_coordinate(self, value: float, attr_name: str) -> float:
        coordinate_char = attr_name[0]
        other_coordinate_value = getattr(self, f"{coordinate_char}start")
        match self.slide_direction, coordinate_char:
            case (SlideDirection.BOTTOM, "y") | (SlideDirection.RIGHT, "x"):
                if value > other_coordinate_value:
                    raise ValueError(f"Invalid {attr_name}")
                return 1 if self.disappear is True else value
            case (SlideDirection.TOP, "y") | (SlideDirection.LEFT, "x"):
                if value < other_coordinate_value:
                    raise ValueError(f"Invalid {attr_name}")
                return -1
            case _:
                return value

    @property
    def forward_offset(self) -> float:
        return self._forward_offset

    @forward_offset.setter
    def forward_offset(self, offset: float) -> None:
        self._forward_offset = self._get_offset(offset)

    @property
    def backward_offset(self) -> float:
        return self._backward_offset

    @backward_offset.setter
    def backward_offset(self, offset: float) -> None:
        self._backward_offset = self._get_offset(offset)

    @property
    def forward_speed(self) -> int:
        return self._forward_speed

    @forward_speed.setter
    def forward_speed(self, speed: int) -> None:
        self._forward_speed = self._get_speed(speed)

    @property
    def backward_speed(self) -> int:
        return self._backward_speed

    @backward_speed.setter
    def backward_speed(self, speed: int) -> None:
        self._backward_speed = self._get_speed(speed)

    def _get_offset(self, offset: float) -> float:
        if self.override_fps is True:
            return offset
        else:
            return round(self.fps_factor / self.fps, self.offset_precision)

    def _get_speed(self, speed: int) -> int:
        return speed if self.override_fps is True else self._get_fps_speed()

    def _get_fps_speed(self) -> int:
        return round(1000 / self.fps)

    def _place(self, x: float, y: float) -> None:
        x = round(x, self.offset_precision)
        y = round(y, self.offset_precision)
        if self.automatic_scaling is True:
            self.place(relx=x, rely=y, relwidth=1, relheight=1)
        else:
            self.place(relx=x, rely=y)

    def _do_animation(self, request: Request) -> None:
        if request.direction is Direction.FORWARD:
            ms = self.forward_speed
        else:
            ms = self.backward_speed
        self._animation(request, ms)

    def _animation(self, request: Request, ms: int) -> None:
        if request.interrupt is True or self._reached(request.direction):
            request.terminated = True
            self._do_next_request()
        else:
            self._set_coordinates(request.direction)
            self._place(self._xactual, self._yactual)
            self.after(ms=ms, func=lambda: self._animation(request, ms))

    def _reached(self, direction: Direction) -> bool:
        match self.slide_direction, direction:
            case (SlideDirection.LEFT, Direction.FORWARD):
                return self._xactual <= self.xend
            case (SlideDirection.LEFT, Direction.BACKWARD):
                return self._xactual >= self.xstart
            case (SlideDirection.RIGHT, Direction.FORWARD):
                return self._xactual >= self.xend
            case (SlideDirection.RIGHT, Direction.BACKWARD):
                return self._xactual <= self.xstart
            case (SlideDirection.TOP, Direction.FORWARD):
                return self._yactual <= self.yend
            case (SlideDirection.TOP, Direction.BACKWARD):
                return self._yactual >= self.ystart
            case (SlideDirection.BOTTOM, Direction.FORWARD):
                return self._yactual >= self.yend
            case (SlideDirection.BOTTOM, Direction.BACKWARD):
                return self._yactual <= self.ystart

    def _set_coordinates(self, direction: Direction) -> None:
        match self.slide_direction, direction:
            case (SlideDirection.LEFT, Direction.FORWARD):
                if self._xactual > self.xend:
                    self._xactual -= self.forward_offset
            case (SlideDirection.LEFT, Direction.BACKWARD):
                if self._xactual < self.xstart:
                    self._xactual += self.backward_offset
            case (SlideDirection.RIGHT, Direction.FORWARD):
                if self._xactual < self.xend:
                    self._xactual += self.forward_offset
            case (SlideDirection.RIGHT, Direction.BACKWARD):
                if self._xactual > self.xstart:
                    self._xactual -= self.backward_offset
            case (SlideDirection.TOP, Direction.FORWARD):
                if self._yactual > self.yend:
                    self._yactual -= self.forward_offset
            case (SlideDirection.TOP, Direction.BACKWARD):
                if self._yactual < self.ystart:
                    self._yactual += self.backward_offset
            case (SlideDirection.BOTTOM, Direction.FORWARD):
                if self._yactual < self.yend:
                    self._yactual += self.forward_offset
            case (SlideDirection.BOTTOM, Direction.BACKWARD):
                if self._yactual > self.ystart:
                    self._yactual -= self.backward_offset
