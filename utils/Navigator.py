"""Screen registry and routing.

Screens implement (all but get_group are optional):
    get_group()           -> displayio.Group
    on_enter(params=None) -> None
    handle_touch(touch)   -> None
    tick(now)             -> None
"""


class Navigator:
    def __init__(self, display):
        self._display = display
        self._screens = {}
        self._active_name = None
        self._active = None

    def register(self, name, screen):
        if not hasattr(screen, "get_group"):
            raise TypeError("screen must implement get_group()")
        self._screens[name] = screen

    def navigate(self, name, params=None):
        if name not in self._screens:
            raise KeyError("unknown screen: " + repr(name))
        screen = self._screens[name]
        if hasattr(screen, "on_enter"):
            screen.on_enter(params)
        self._display.root_group = screen.get_group()
        self._active_name = name
        self._active = screen

    @property
    def active(self):
        return self._active

    @property
    def active_name(self):
        return self._active_name

    def handle_touch(self, touch):
        if self._active is not None and hasattr(self._active, "handle_touch"):
            self._active.handle_touch(touch)

    def tick(self, now):
        if self._active is not None and hasattr(self._active, "tick"):
            self._active.tick(now)
