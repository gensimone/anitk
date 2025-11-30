import logging
import math
from customtkinter import CTkBaseClass
from actkinter.base import BaseFrame, Request
from actkinter.enums import Axis, Orientation, Direction


logger = logging.getLogger(__name__)


class ResizableFrame(BaseFrame):
    def __init__(
        self,
        initial_width: float = 1,
        initial_height: float = 1,
        final_width: float = 500,
        final_height: float = 250,

        hforward_animation_speed: int = 10,
        vforward_animation_speed: int = 10,
        hbackward_animation_speed: int = 10,
        vbackward_animation_speed: int = 10,

        hforward_offset: float = 1.0,
        vforward_offset: float = 1.0,
        hbackward_offset: float = 1.0,
        vbackward_offset: float = 1.0,

        orientation: Orientation = Orientation.CENTER,
        relative_expansion: bool = True,

        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.initial_width = initial_width
        self.initial_height = initial_height
        self.final_width = final_width
        self.final_height = final_height

        self.configure(width=self.final_width, height=self.final_height)
        self.grid_rowconfigure(index=0, minsize=self.final_height)
        self.grid_columnconfigure(index=0, minsize=self.final_width)

        if self._opened:
            self._actual_width = self.final_width
            self._actual_height = self.final_height
        else:
            self._actual_width = self.initial_width
            self._actual_height = self.initial_height

        self.orientation = orientation
        self.relative_expansion = relative_expansion
        self._incremental_offset_factor = 500

        self._h_calls_counter = 0
        self._v_calls_counter = 0

        self._h_abs_distance = self._get_horizontal_distance()
        self._v_abs_distance = self._get_vertical_distance()

        if self._h_abs_distance > self._v_abs_distance:
            self.hforward_offset = hforward_offset
            self.vforward_offset = vforward_offset
            self.hbackward_offset = hbackward_offset
            self.vbackward_offset = vbackward_offset

        else:
            self.vforward_offset = vforward_offset
            self.hforward_offset = hforward_offset
            self.vbackward_offset = vbackward_offset
            self.hbackward_offset = hbackward_offset

        self.hforward_animation_speed = hforward_animation_speed
        self.vforward_animation_speed = vforward_animation_speed
        self.hbackward_animation_speed = hbackward_animation_speed
        self.vbackward_animation_speed = vbackward_animation_speed

        self._h_abs_forward_required_calls = self._get_relative_required_calls(
            self._h_abs_distance,
            Direction.FORWARD,
            Axis.HORIZONTAL
        )

        self._h_abs_backward_required_calls = self._get_relative_required_calls(
            self._h_abs_distance,
            direction=Direction.BACKWARD,
            axis=Axis.HORIZONTAL
        )

        self._v_abs_forward_required_calls = self._get_relative_required_calls(
            self._v_abs_distance,
            direction=Direction.FORWARD,
            axis=Axis.VERTICAL
        )

        self._v_abs_backward_required_calls = self._get_relative_required_calls(
            self._v_abs_distance,
            direction=Direction.BACKWARD,
            axis=Axis.VERTICAL
        )

        logger.debug(f"orientation:        {self.orientation}")
        logger.debug(f"relative_expansion: {self.relative_expansion}")

        logger.debug(f"initial_width:  {self.initial_width}")
        logger.debug(f"initial_height: {self.initial_height}")
        logger.debug(f"final_width:    {self.final_width}")
        logger.debug(f"final_height:   {self.final_height}")
        logger.debug(f"_actual_width:  {self._actual_width}")
        logger.debug(f"_actual_height: {self._actual_height}")

        logger.debug(f"hforward_animation_speed:  {self.hforward_animation_speed}")
        logger.debug(f"vforward_animation_speed:  {self.vforward_animation_speed}")
        logger.debug(f"hbackward_animation_speed: {self.hbackward_animation_speed}")
        logger.debug(f"vbackward_animation_speed: {self.vbackward_animation_speed}")

        logger.debug(f"hforward_offset:  {self.hforward_offset}")
        logger.debug(f"vforward_offset:  {self.vforward_offset}")
        logger.debug(f"hbackward_offset: {self.hbackward_offset}")
        logger.debug(f"vbackward_offset: {self.vbackward_offset}")

        logger.debug(f"_h_abs_forward_required_calls:  {self._h_abs_forward_required_calls}")
        logger.debug(f"_v_abs_forward_required_calls:  {self._v_abs_forward_required_calls}")
        logger.debug(f"_h_abs_backward_required_calls: {self._h_abs_backward_required_calls}")
        logger.debug(f"_v_abs_backward_required_calls: {self._v_abs_backward_required_calls}")
        logger.debug(f"_h_abs_distance: {self._h_abs_distance}")
        logger.debug(f"_v_abs_distance: {self._v_abs_distance}")
        logger.debug(f"_h_calls_counter: {self._h_calls_counter}")
        logger.debug(f"_v_calls_counter: {self._v_calls_counter}")

    def _get_fps_animation_speed(self):
        result = round(1000 / (self.fps + 500))
        return 1 if not result else result

    @property
    def initial_width(self) -> float:
        return self._initial_width

    @initial_width.setter
    def initial_width(self, value: float) -> None:
        self._initial_width = self._get_dimension(value, "_initial_width")

    @property
    def initial_height(self) -> float:
        return self._initial_height

    @initial_height.setter
    def initial_height(self, value: float) -> None:
        self._initial_height = self._get_dimension(value, "_initial_height")

    @property
    def final_width(self) -> float:
        return self._final_width

    @final_width.setter
    def final_width(self, value: float) -> None:
        self._final_width = self._get_dimension(value, "_final_width")

    @property
    def final_height(self) -> float:
        return self._final_height

    @final_height.setter
    def final_height(self, value: float) -> None:
        self._final_height = self._get_dimension(value, "_final_height")

    def _get_dimension(self, value: float, attr_name: str) -> float:
        pdimension_attr = attr_name[1:]
        value = float(value)
        end_other_attr = "height" if pdimension_attr[6] == "h" else "width"

        if pdimension_attr[0] == "f":
            other_dimension_attr = "initial_" + end_other_attr
            if value < getattr(self, other_dimension_attr):
                raise ValueError(
                    f"{pdimension_attr} must be greater than or equal to {other_dimension_attr}"
                )
            return value
        else:
            if value <= 0:
                raise ValueError(f"{pdimension_attr} must be greater than zero")
            return value

    @property
    def vforward_offset(self) -> float:
        return self._vforward_offset

    @vforward_offset.setter
    def vforward_offset(self, value: float) -> None:
        self._vforward_offset = self._get_offset(value, "_vforward_offset")

    @property
    def hforward_offset(self) -> float:
        return self._hforward_offset

    @hforward_offset.setter
    def hforward_offset(self, value: float) -> None:
        self._hforward_offset = self._get_offset(value, "_hforward_offset")

    @property
    def vbackward_offset(self) -> float:
        return self._vbackward_offset

    @vbackward_offset.setter
    def vbackward_offset(self, value: float) -> None:
        self._vbackward_offset = self._get_offset(value, "_vbackward_offset")

    @property
    def hbackward_offset(self) -> float:
        return self._hbackward_offset

    @hbackward_offset.setter
    def hbackward_offset(self, value: float) -> None:
        self._hbackward_offset = self._get_offset(value, "_hbackward_offset")

    def _get_offset(self, value: float, attr_name: str) -> float:
        value = float(value)
        if value <= 0:
            raise ValueError(f"'{attr_name[1:]}' must be a positive number.")

        if attr_name[2] == "f":
            direction = "forward"
        else:
            direction = "backward"

        if (
            self._relative_expansion is False
            or (self._relative_expansion is True and self._h_abs_distance >= self._v_abs_distance)
        ):
            return value if self.override_fps is True else self._get_fps_offset()

        else:
            if attr_name[1] == "v":
                div = self._h_abs_distance / self._v_abs_distance
                offset = getattr(self, f"h{direction}_offset")
            else:
                div = self._v_abs_distance / self._h_abs_distance
                offset = getattr(self, f"v{direction}_offset")
            return round(offset / div, self.offsets_precision)

    def _get_fps_offset(self) -> float:
        return round(self.fps_factor / self.fps, self.offsets_precision) + 5

    @property
    def widget(self) -> CTkBaseClass:
        return self._widget

    @widget.setter
    def widget(self, value: CTkBaseClass) -> None:
        if not isinstance(value, CTkBaseClass):
            raise TypeError(f"Invalid input type: {type(value)}. Expected input type: CTkBaseClass")
        self._widget = value
        self._widget.configure(width=self._actual_width, height=self._actual_height)
        self.widget.grid(row=0, column=0, sticky=self.orientation.value)

    def grid(self, *args, **kwargs) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        super().grid(*args, **kwargs)
        self.final_width = self.cget("width")
        self.final_height = self.cget("height")
        self.widget.grid(row=0, column=0, sticky=self.orientation.value)

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, value: Orientation) -> None:
        if isinstance(value, Orientation) is False:
            raise TypeError(f"Invalid input type: {type(value)}. Expected input type: Orientaion")
        self._orientation = value

    @property
    def relative_expansion(self) -> bool:
        return self._relative_expansion

    @relative_expansion.setter
    def relative_expansion(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"Invalid input type: {type(value)}. Expected input type: bool")
        self._relative_expansion = value

    def _clear_animation_runtime_data(self):
        self.h_calls_counter = 0
        self.v_calls_counter = 0
        self.backward_required_calls = self._get_required_calls(Direction.BACKWARD)
        self.forward_required_calls = self._get_required_calls(Direction.FORWARD)

    def _get_relative_required_calls(self, distance: float, direction: Direction, axis: Axis) -> int:
        if self._enable_animation is True:
            attr = ResizableFrame._get_attr(direction, axis)
            return math.ceil(distance / getattr(self, f"{attr}_offset"))
        else:
            return 1

    def _get_required_calls(self, direction: Direction) -> int:
        return max(
            self._get_relative_required_calls(self._get_horizontal_distance(), direction, Axis.HORIZONTAL),
            self._get_relative_required_calls(self._get_vertical_distance(), direction, Axis.VERTICAL)
        )

    def _get_horizontal_distance(self) -> float:
        return self._final_width - self._initial_width

    def _get_vertical_distance(self) -> float:
        return self._final_height - self._initial_height

    def _get_current_horizontal_distance(self) -> float:
        return self._final_width - self._actual_width

    def _get_current_vertical_distance(self) -> float:
        return self._final_height - self._actual_height

    def _reconfigure_widget_dimension(self, direction: Direction, axis: Axis) -> None:
        match direction, axis:
            case (Direction.FORWARD, Axis.HORIZONTAL):
                if self._actual_width > self.initial_width:
                    self._actual_width -= self.hforward_offset
            case (Direction.BACKWARD, Axis.HORIZONTAL):
                if self._actual_width < self.final_width:
                    self._actual_width += self.hbackward_offset
            case (Direction.FORWARD, Axis.VERTICAL):
                if self._actual_height > self.initial_height:
                    self._actual_height -= self.vforward_offset
            case (Direction.BACKWARD, Axis.VERTICAL):
                if self._actual_height < self.final_height:
                    self._actual_height += self.vbackward_offset
        self.widget.configure(width=self._actual_width, height=self._actual_height)
        logger.debug(f"width: {self._actual_width}; height: {self._actual_height}")

    def _close_operation(self, direction: Direction) -> None:
        if direction is Direction.FORWARD:
            self.widget.configure(width=self.initial_width, height=self.initial_height)
        else:
            self.widget.configure(width=self.final_width, height=self.final_height)
        self._h_calls_counter = 0
        self._v_calls_counter = 0
        super()._close_operation(direction)

    def _get_animation_speed(self, direction: Direction, axis: Axis) -> int:
        attr = ResizableFrame._get_attr(direction, axis)
        return getattr(self, f"{attr}_animation_speed")

    @staticmethod
    def _get_attr(direction: Direction, axis: Axis) -> str:
        match direction, axis:
            case (Direction.FORWARD, Axis.HORIZONTAL):
                return "hforward"
            case (Direction.FORWARD, Axis.VERTICAL):
                return "vforward"
            case (Direction.BACKWARD, Axis.HORIZONTAL):
                return "hbackward"
            case (Direction.BACKWARD, Axis.VERTICAL):
                return "vbackward"
            case _:
                raise ValueError(f"Unexpected input: {direction}; {axis}")

    def _do_animation(self, request: Request) -> None:
        if request.direction is Direction.FORWARD:
            vms = self.vforward_animation_speed
            hms = self.hforward_animation_speed
            vrc = self._v_abs_forward_required_calls
            hrc = self._h_abs_forward_required_calls
        else:
            vms = self.vbackward_animation_speed
            hms = self.hbackward_animation_speed
            vrc = self._v_abs_backward_required_calls
            hrc = self._h_abs_backward_required_calls

        # """ absolute required calls """
        # h_abs_distance = self._get_horizontal_distance()
        # h_abs_required_calls = self._get_relative_required_calls(
        #     distance=h_abs_distance, direction=request.direction, axis=Axis.HORIZONTAL
        # )
        # v_abs_distance = self._get_vertical_distance()
        # v_abs_required_calls = self._get_relative_required_calls(
        #     distance=v_abs_distance, direction=request.direction, axis=Axis.VERTICAL
        # )

        """ Relative required calls """
        h_rel_distance = self._get_current_horizontal_distance()
        h_rel_required_calls = self._get_relative_required_calls(
            distance=h_rel_distance, direction=request.direction, axis=Axis.HORIZONTAL
        )
        v_rel_distance = self._get_current_vertical_distance()
        v_rel_required_calls = self._get_relative_required_calls(
            distance=v_rel_distance, direction=request.direction, axis=Axis.VERTICAL
        )

        self._v_calls_counter = vrc - v_rel_required_calls
        self._h_calls_counter = hrc - h_rel_required_calls

        logger.debug(f"_v_calls_counter: {self._v_calls_counter}")
        logger.debug(f"_h_calls_counter: {self._h_calls_counter}")

        self.after(ms=0, func=lambda: self._animation(
            request=request,
            axis=Axis.VERTICAL,
            calls_counter_attr_name="_v_calls_counter",
            required_calls=vrc,
            ms=vms
        ))

        self.after(ms=0, func=lambda: self._animation(
            request=request,
            axis=Axis.HORIZONTAL,
            calls_counter_attr_name="_h_calls_counter",
            required_calls=hrc,
            ms=hms,
        ))

    def _animation(
        self,
        request: Request,
        required_calls: int,
        axis: Axis,
        calls_counter_attr_name: str,
        ms: int
    ) -> None:
        calls_counter = getattr(self, calls_counter_attr_name)
        if request.interrupt is True:
            request.terminated = True
            self._next_request()

        elif calls_counter >= required_calls:
            self._close_operation(request.direction)
            request.terminated = True
            self._next_request()

        else:
            setattr(self, calls_counter_attr_name, calls_counter + 1)
            self._reconfigure_widget_dimension(request.direction, axis)
            self.after(ms=ms, func=lambda: self._animation(
                request=request,
                required_calls=required_calls,
                axis=axis,
                calls_counter_attr_name=calls_counter_attr_name,
                ms=ms
            ))
