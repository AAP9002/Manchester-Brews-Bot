import os

_WMO_CONDITIONS = {
    0:  "Clear",
    1:  "Mostly Clear",
    2:  "Partly Cloudy",
    3:  "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Heavy Rain",
    71: "Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Showers",
    81: "Showers",
    82: "Heavy Showers",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}

class WeatherManager:
    def __init__(self, send, app_state):
        self._send = send
        self._state = app_state

    def fetch(self):
        if self._state and not self._state.get("wifi_connected", False):
            print("[Weather] No WiFi - skipping fetch")
            return

        lat = os.getenv("WEATHER_LAT", "53.48")
        lon = os.getenv("WEATHER_LON", "-2.24")

        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=" + str(lat) +
            "&longitude=" + str(lon) +
            "&current=temperature_2m,weather_code"
            "&daily=precipitation_probability_max"
            "&temperature_unit=celsius"
            "&timezone=auto"
            "&forecast_days=1"
        )

        print("[Weather] Fetching from Open-Meteo...")
        ok, data = self._send.get(url)

        if not ok or data is None:
            print("[Weather] No data returned")
            return

        try:
            current = data["current"]
            temp = current["temperature_2m"]
            code = current["weather_code"]
            condition = _WMO_CONDITIONS.get(code, "Unknown")

            rain_chance = None
            try:
                rain_chance = data["daily"]["precipitation_probability_max"][0]
            except Exception:
                pass

            if self._state is not None:
                self._state["weather_temp"] = temp
                self._state["weather_condition"] = condition
                self._state["weather_rain_chance"] = rain_chance

            print("[Weather] " + str(temp) + "C - " + condition + " - Rain: " + str(rain_chance) + "%")
        except Exception as e:
            print("[Weather] Parse error: " + str(e))
