import math, type_enforced, uuid


def unique_id():
    """
    Generates a unique identifier.
    """
    return str(uuid.uuid4())


class Thunk(type_enforced.utils.Partial):
    def __call__(self, *args, **kwargs):
        new_args = self.__args__ + args
        new_kwargs = {**self.__kwargs__, **kwargs}
        self.__arity__ = self.__getArity__(new_args, new_kwargs)
        if self.__arity__ < 0:
            self.__exception__("Too many arguments were supplied")
        if self.__arity__ == 0 and len(args) == 0 and len(kwargs) == 0:
            results = self.__fn__(*new_args, **new_kwargs)
            return results
        return Thunk(
            self.__fn__,
            *new_args,
            **new_kwargs,
        )

    def __get__(self, instance, owner):
        def bind(*args, **kwargs):
            if instance is not None and self.__arity__ == self.__fnArity__:
                return self.__call__(instance, *args, **kwargs)
            else:
                return self.__call__(*args, **kwargs)

        return bind


@type_enforced.Enforcer(enabled=True)
class Shape:
    @staticmethod
    def circle(radius: int, points: int = 6, round_to: int = 2) -> list:
        """
        Returns a list of addative coordinates that form a circle around a given point.
        """
        return [
            [
                round(radius * math.cos(2 * math.pi / points * i), round_to),
                round(radius * math.sin(2 * math.pi / points * i), round_to),
            ]
            for i in range(points)
        ]

    @staticmethod
    def rectangle(
        x_len: float | int, y_len: float | int, round_to: int = 2
    ) -> list:
        """
        Returns a list of addative coordinates that form a rectangle around a given point.
        """
        return [
            [round(x_len / 2, round_to), round(y_len / 2, round_to)],
            [round(-x_len / 2, round_to), round(y_len / 2, round_to)],
            [round(-x_len / 2, round_to), round(-y_len / 2, round_to)],
            [round(x_len / 2, round_to), round(-y_len / 2, round_to)],
        ]


class RectangleMoverUtils:
    @staticmethod
    def moving_segment_overlap_intervals(
        seg_start: int | float,
        seg_end: int | float,
        t_start: int | float,
        t_end: int | float,
        shift: int | float,
    ):
        """
        Calculates the time intervals during which a moving 1D line segment overlaps with each unit-length
        integer-aligned range along the x-axis.

        Args:

            - seg_start (int|float): Initial position of the left end of the line segment.
            - seg_end (int|float): Initial position of the right end of the line segment.
            - t_start (int|float): Start time of the motion.
            - t_end (int|float): End time of the motion.
            - shift (int|float): Total distance the line segment moves along the x-axis during [t_start, t_end].

        Returns:

            - dict[int, tuplie(int|float,int|float)]: A dictionary mapping each integer `i` to the time interval [t_in, t_out]
                                    during which any part of the line overlaps the range [i, i+1).
                                    Only includes ranges with non-zero overlap duration.
        """
        duration = t_end - t_start
        velocity = shift / duration if duration != 0 else 0

        result = {}

        final_start = seg_start + shift
        final_end = seg_end + shift
        global_min = min(seg_start, final_start)
        global_max = max(seg_end, final_end)

        for i in range(int(global_min) - 1, int(global_max) + 2):
            if velocity == 0:
                if seg_end > i and seg_start < i + 1 and t_start < t_end:
                    result[i] = (t_start, t_end)
                continue
            # Solve for times when the line enters and exits overlap with [i, i+1)
            t1 = (i - seg_end) / velocity + t_start
            t2 = (i + 1 - seg_start) / velocity + t_start
            entry_time = max(min(t1, t2), t_start)
            exit_time = min(max(t1, t2), t_end)

            if exit_time > entry_time:
                result[i] = (entry_time, exit_time)

        return result

    @staticmethod
    def moving_rectangle_overlap_intervals(
        x_start: float | int,
        x_end: float | int,
        y_start: float | int,
        y_end: float | int,
        x_shift: float | int,
        y_shift: float | int,
        t_start: float | int,
        t_end: float | int,
    ):
        """
        Calculates the time intervals during which a moving rectangle overlaps with each unit-length
        integer-aligned range along the x and y axes.

        Args:

            - x_start (float|int): Initial position of the left end of the rectangle along the x-axis.
            - x_end (float|int): Initial position of the right end of the rectangle along the x-axis.
            - y_start (float|int): Initial position of the bottom end of the rectangle along the y-axis.
            - y_end (float|int): Initial position of the top end of the rectangle along the y-axis.
            - x_shift (float|int): Total distance the rectangle moves along the x-axis during [t_start, t_end].
            - y_shift (float|int): Total distance the rectangle moves along the y-axis during [t_start, t_end].
            - t_start (float|int): Start time of the motion.
            - t_end (float|int): End time of the motion.

        Returns:

            - dict[tuple(int,int),tuple(int|float,int|float)]: A dictionary mapping each integer (i,j) to the time interval [t_in, t_out]
                during which any part of the rectangle overlaps the range [i, i+1) x [j, j+1).
                Only includes ranges with non-zero overlap duration.

        """
        x_intervals = RectangleMoverUtils.moving_segment_overlap_intervals(
            seg_start=x_start,
            seg_end=x_end,
            t_start=t_start,
            t_end=t_end,
            shift=x_shift,
        )
        y_intervals = RectangleMoverUtils.moving_segment_overlap_intervals(
            seg_start=y_start,
            seg_end=y_end,
            t_start=t_start,
            t_end=t_end,
            shift=y_shift,
        )
        result = {}
        for x_key, x_interval in x_intervals.items():
            for y_key, y_interval in y_intervals.items():
                # Only add intervals with time overlap
                if (
                    x_interval[1] > y_interval[0]
                    and y_interval[1] > x_interval[0]
                ):
                    result[(x_key, y_key)] = (
                        max(x_interval[0], y_interval[0]),
                        min(x_interval[1], y_interval[1]),
                    )

        return result

    @staticmethod
    def moving_shape_overlap_intervals(
        x_coord: float | int,
        y_coord: float | int,
        x_shift: float | int,
        y_shift: float | int,
        t_start: float | int,
        t_end: float | int,
        shape: list[list[float | int]],
    ):
        """
        Calculates the time intervals during which a moving shape overlaps with each unit-length
        integer-aligned range along the x and y axes.

        Note: This converts each shape into a full bounding box rectangle and then uses the rectangle overlap function to calculate the intervals.

        Args:

            - x_coord (float|int): Initial x-coordinate of the shape's center.
            - y_coord (float|int): Initial y-coordinate of the shape's center.
            - x_shift (float|int): Total distance the shape moves along the x-axis during [t_start, t_end].
            - y_shift (float|int): Total distance the shape moves along the y-axis during [t_start, t_end].
            - t_start (float|int): Start time of the motion.
            - t_end (float|int): End time of the motion.
            - shape (list[list[float|int]]): List of coordinates representing the shape's vertices relative to its center.

        Returns:

            - dict[tuple(int,int),tuple(int|float,int|float)]: A dictionary mapping each integer (i,j) to the time interval [t_in, t_out]
                                    during which any part of the shape overlaps the range [i, i+1) x [j, j+1).
                                    Only includes ranges with non-zero overlap duration.
        """
        # Return the overlap intervals for a rectangle
        return RectangleMoverUtils.moving_rectangle_overlap_intervals(
            x_start=min([x_coord + coord[0] for coord in shape]),
            x_end=max([x_coord + coord[0] for coord in shape]),
            y_start=min([y_coord + coord[1] for coord in shape]),
            y_end=max([y_coord + coord[1] for coord in shape]),
            x_shift=x_shift,
            y_shift=y_shift,
            t_start=t_start,
            t_end=t_end,
        )
