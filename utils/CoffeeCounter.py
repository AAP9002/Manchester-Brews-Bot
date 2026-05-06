import os

class CoffeeCounter:
    def __init__(self, send, app_state):
        self._send = send
        self._state = app_state

    def increment(self):
        if self._state is None:
            return
        self._state["coffee_count"] = self._state.get("coffee_count", 0) + 1

    def sync(self):
        if self._state is None:
            return
        if not self._state.get("wifi_connected", False):
            print("[CoffeeCounter] No WiFi - skipping sync")
            return
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        if not sheet_url:
            return
        try:
            ok, body = self._send.get(sheet_url + "?action=log")
            if not ok or not body:
                return
            count = body.get("count")
            if count is not None:
                self._state["coffee_count"] = count
        except Exception as e:
            print("Coffee sync error: " + str(e))

    def fetch(self):
        if self._state is None:
            return
        if not self._state.get("wifi_connected", False):
            print("[CoffeeCounter] No WiFi - skipping fetch")
            return
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        if not sheet_url:
            return
        try:
            ok, body = self._send.get(sheet_url)
            if not ok or not body:
                return
            count = body.get("count")
            if count is not None:
                self._state["coffee_count"] = count
        except Exception as e:
            print("Coffee fetch error: " + str(e))

    def get_count(self):
        if self._state is None:
            return 0
        return self._state.get("coffee_count", 0)
