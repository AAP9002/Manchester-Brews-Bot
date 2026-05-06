"""Slack helper.

A single Slack Workflow webhook (SEND_MESSAGE_SLACK_WEBHOOK) receives all
messages. Per-action message content lives in utils.config.SLACK_MESSAGES
and is selected by a Msg key string.
"""

import os
from utils.config import SLACK_MESSAGES

_WEBHOOK = os.getenv("SEND_MESSAGE_SLACK_WEBHOOK")


class Msg:
    """String keys into SLACK_MESSAGES."""
    LOW_ON_BEANS = "low_on_beans"
    BREWING      = "brewing"
    READY        = "ready"


def post(send_request, key, **fmt):
    """Post the SLACK_MESSAGES[key] template to the single webhook.

    `**fmt` is forwarded to str.format on the template (e.g. name=...).
    Returns (ok, body) per SendRequest contract.
    """
    template = SLACK_MESSAGES[key]
    body = template.format(**fmt) if fmt else template
    return send_request.post(_WEBHOOK, {"messageContent": body})
