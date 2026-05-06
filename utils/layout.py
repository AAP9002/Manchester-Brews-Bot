"""Text and layout primitives.

Stateless helpers for positioning labels and computing text metrics
against terminalio.FONT (5x8 fixed-width).
"""

import terminalio
from adafruit_display_text import label

CHAR_BASE_WIDTH = 5
CHAR_BASE_HEIGHT = 8
CHAR_BASE_GAP = 1


def get_text_width(text, scale=1):
    """Pixel width of `text` rendered at `scale` using terminalio.FONT."""
    if not text:
        return 0
    return len(text) * (CHAR_BASE_WIDTH * scale) + (len(text) - 1) * (CHAR_BASE_GAP * scale)


def resolve_text_position(value, parent_size, offset):
    """Resolve a position value, supporting the 'center' sentinel.

    value: int pixel coord, or the string 'center'.
    parent_size: width/height of the parent for centering math.
    offset: extra delta applied (e.g. text-half-width for horizontal centering).
    """
    if value == "center":
        return parent_size // 2 + offset
    return value + offset


def make_text_label(text, scale=1, color=0xDDDDDD, x=0, y=0,
                    parent_width=320, parent_height=240):
    """Create a terminalio.FONT label, optionally centred via the 'center' sentinel.

    x or y may be:
        int      - exact pixel coordinate
        'center' - centred on the parent dimension
    """
    text_label = label.Label(terminalio.FONT, text=text, color=color)
    text_label.scale = scale

    text_width = get_text_width(text, scale)
    horizontal_offset = -text_width // 2 if x == "center" else 0
    vertical_offset = (CHAR_BASE_HEIGHT // 2) * scale if y == "center" else 0

    text_label.x = int(resolve_text_position(x, parent_width, horizontal_offset))
    text_label.y = int(resolve_text_position(y, parent_height, vertical_offset))
    return text_label


def truncate_to_width(text, scale, max_width):
    """Truncate `text` with an ellipsis so its rendered width <= max_width."""
    if get_text_width(text, scale) <= max_width:
        return text
    if max_width <= get_text_width("...", scale):
        return ""

    out = text
    while out and get_text_width(out + "...", scale) > max_width:
        out = out[:-1]
    return out + "..."


def split_title_lines(text, scale, max_width, max_lines=2):
    """Wrap `text` into up to `max_lines` lines respecting word boundaries.

    The final line is ellipsis-truncated if it would still overflow.
    Returns a list of strings (length 1..max_lines).
    """
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if get_text_width(candidate, scale) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
                current = word
            else:
                lines.append(truncate_to_width(word, scale, max_width))
                current = ""
        if len(lines) == max_lines:
            break

    if len(lines) < max_lines and current:
        lines.append(current)

    if not lines:
        return [""]

    if len(lines) > max_lines:
        lines = lines[:max_lines]
    lines[-1] = truncate_to_width(lines[-1], scale, max_width)
    return lines
