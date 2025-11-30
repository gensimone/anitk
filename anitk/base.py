import logging
from typing import Optional
from abc import abstractmethod, ABC
from customtkinter import CTkFrame as Frame
from actkinter.enums import Direction


logger = logging.getLogger(__name__)


class BaseRequest:
    def __init__(
        self,
        terminated: bool = False,
        interrupt: bool = False
    ):
        self.terminated = terminated
        self.interrupt = interrupt

class Request(BaseRequest):
    def __init__(self, direction: Direction, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.direction = direction


class BaseFrame(Frame, ABC):
    def __init__(
        self,
        enable_animation: bool = True,
        ignore_inputs: bool = False,
        fps: int = 60,
        fps_factor: float = 1.1,
        override_fps: bool = False,
        offset_precision: int = 6,
        opened: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._opened = opened
        self.enable_animation = enable_animation
        self.ignore_inputs = ignore_inputs
        self.fps = fps
        self.fps_factor = fps_factor
        self.override_fps = override_fps
        self.offset_precision = offset_precision
        self._request = Request(
            terminated=True,
            direction=Direction.FORWARD if opened is True else Direction.BACKWARD
        )
        self._next_request: Optional[Request] = None

    def _ignore_request(self, direction: Direction) -> bool:
        return (
            self._request.terminated is False and self.ignore_inputs is True
            or self._request.direction == direction
        )

    def _put_request(self, direction: Direction) -> None:
        if self._ignore_request(direction) is False:
            request = Request(direction)
            if self.ignore_inputs is True:
                self._request = request
                self._do_animation(request)
            else:
                self._next_request = request
                if self._request.terminated is False:
                    self._request.interrupt = True
                else:
                    self._do_next_request()

    def _do_next_request(self) -> None:
        if self._next_request is not None:
            self._request = self._next_request
            self._next_request = None
            if self._request.direction is Direction.FORWARD:
                self._backward_animation_reached = False
            else:
                self._forward_animation_reached = False
            self._do_animation(self._request)

    def backward(self) -> None:
        self._put_request(direction=Direction.BACKWARD)

    def forward(self) -> None:
        self._put_request(direction=Direction.FORWARD)

    def do_animation(self) -> None:
        match self._request.direction:
            case Direction.BACKWARD:
                self.forward()
            case Direction.FORWARD:
                self.backward()

    @abstractmethod
    def _do_animation(self, request: Request) -> None:
        """ """
