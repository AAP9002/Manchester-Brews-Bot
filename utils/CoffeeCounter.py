import os
from utils.SendRequest import SendRequest

class CoffeeCounter:
    app_state = None

    @staticmethod
    def increment():
        if CoffeeCounter.app_state is None:
            return
        CoffeeCounter.app_state["coffee_count"] = CoffeeCounter.app_state.get("coffee_count", 0) + 1

    @staticmethod
    def sync():
        if CoffeeCounter.app_state is None:
            return
        if not CoffeeCounter.app_state.get("wifi_connected", False):
            print("[CoffeeCounter] No WiFi - skipping sync")
            return
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        if not sheet_url:
            return
        try:
            data = SendRequest.get(sheet_url + "?action=log")
            if data and "count" in data:
                CoffeeCounter.app_state["coffee_count"] = data["count"]
        except Exception as e:
            print("Coffee sync error: " + str(e))

    @staticmethod
    def fetch():
        if CoffeeCounter.app_state is None:
            return
        if not CoffeeCounter.app_state.get("wifi_connected", False):
            print("[CoffeeCounter] No WiFi - skipping fetch")
            return
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        if not sheet_url:
            return
        try:
            data = SendRequest.get(sheet_url)
            if data and "count" in data:
                CoffeeCounter.app_state["coffee_count"] = data["count"]
        except Exception as e:
            print("Coffee fetch error: " + str(e))

    @staticmethod
    def get_count():
        if CoffeeCounter.app_state is None:
            return 0
        return CoffeeCounter.app_state.get("coffee_count", 0)
