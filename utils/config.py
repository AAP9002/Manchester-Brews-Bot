# utils/config.py

DISPLAY = {
    "width": 320,
    "height": 240,
}

COLOURS = {
    "blue":    0x2563EB,
    "red":     0xEF4444,
    "teal":    0x14B8A6,
    "success": 0x16A34A,
    "dark":    0x111827,
    "white":   0xFFFFFF,
    "muted":   0x6B7280,
}

TIMING = {
    "success_dismiss": 2.5,    # seconds the SuccessScreen stays before returning home
    "wifi_poll":       5.0,    # seconds between wifi state checks
    "tap_debounce":    0.3,    # min seconds between taps on the same control
    "reconnect_poll":  5.0,    # seconds between reconnect attempts on NoConnectionScreen
}

MESSAGES = {
    # The {name} placeholder is filled at runtime from env var
    # LOW_BEANS_PERSON (default "Someone" if unset). HomeScreen does
    # the .format() — config.py stays constants-only.
    "low_on_beans": (
        "{name} has been peer-pressured effectively...",
        "beans should be with you shortly",
    ),
    "log_intake_default": "Cup logged.",
    "brewing":            "Brewing announced",
    "ready":              "Ready announced",
    "no_connection":      "No internet connection",
}

SLACK_MESSAGES = {
    # Posted to SEND_MESSAGE_SLACK_WEBHOOK by utils/slack.py.
    "low_on_beans": "Beans are running low — please refill",
    "brewing":      "Coffee is brewing",
    "ready":        "Coffee is ready",
}

IMAGES = {
    "send_icon":       "/images/announcement.bmp",
    "low_beans_icon":  "/images/low-beans.bmp",
    "log_intake_icon": "/images/log-intake.bmp",
    "brewing_icon":    "/images/loading.bmp",
    "ready_icon":      "/images/coffee-done.bmp",
    "back_icon":       "/images/back.bmp",
}
