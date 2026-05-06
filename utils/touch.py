"""Touch primitives for the 320x240 display + CST8xx capacitive driver.

normalize()    — coordinate rotation (raw CST8xx → display coords).
TouchTracker   — edge-triggered single-touch poller.
"""

DISPLAY_HEIGHT = 240


def normalize(raw_touch):
    """Convert a raw touch to (tx, ty) in display coordinates.

    raw_touch may be a tuple (x, y, ...) or a dict {"x": ..., "y": ...}
    depending on driver version. Support both.
    """
    if isinstance(raw_touch, dict):
        raw_x = raw_touch["x"]
        raw_y = raw_touch["y"]
    else:
        raw_x = raw_touch[0]
        raw_y = raw_touch[1]
    return (raw_y, DISPLAY_HEIGHT - raw_x)


class TouchTracker:
    """Yields one normalized touch on the rising edge of a press.

    Usage in the main loop:
        tracker = TouchTracker(ctp)
        while True:
            touch = tracker.poll()
            if touch is not None:
                navigator.active.handle_touch(touch)
    """

    def __init__(self, ctp):
        self._ctp = ctp
        self._prev = False

    def poll(self):
        touching = self._ctp.touched
        result = None
        if touching and not self._prev:
            touches = self._ctp.touches
            if touches:
                result = normalize(touches[0])
        self._prev = touching
        return result
