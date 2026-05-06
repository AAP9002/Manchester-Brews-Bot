import adafruit_requests
import adafruit_connection_manager
import wifi
import gc


class SendRequest:
    def __init__(self, app_state):
        self._state = app_state
        self._pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
        self._session = self._build_session(self._pool)

    @staticmethod
    def _build_session(pool=None):
        if pool is None:
            pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
        return adafruit_requests.Session(pool, ssl_context)

    def _cleanup(self, response):
        if response is not None:
            try:
                response.close()
            except Exception as e:
                print("[Cleanup] response close error: " + str(e))
        try:
            adafruit_connection_manager.connection_manager_close_all(self._pool)
        except Exception as e:
            print("[Cleanup] error: " + str(e))
        gc.collect()

    def post(self, webhook_url, payload=None, headers=None):
        if not self._state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return (False, None)
        if payload is None:
            payload = {}
        response = None
        try:
            response = self._session.post(webhook_url, json=payload, headers=headers)
            try:
                data = response.json()
            except Exception:
                data = None
            print(data)
            return (True, data)
        except Exception as e:
            print("POST error: " + str(e))
            return (False, None)
        finally:
            self._cleanup(response)

    def post_sheets(self, url):
        if not self._state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return (False, None)
        response = None
        try:
            print("[Sheets] POSTing to: " + url[:60])
            response = self._session.post(url, json={}, headers={"Connection": "close"})
            status = response.status_code
            body = response.text
            print("[Sheets] status=" + str(status))
            print("[Sheets] body=" + str(body))
            return (True, None)
        except Exception as e:
            print("[Sheets] POST error: " + str(e))
            return (False, None)
        finally:
            self._cleanup(response)

    def get(self, url):
        if not self._state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return (False, None)
        response = None
        try:
            response = self._session.get(url, headers={"Connection": "close"})
            try:
                data = response.json()
            except Exception:
                data = None
            print(data)
            return (True, data)
        except Exception as e:
            print("GET error: " + str(e))
            return (False, None)
        finally:
            self._cleanup(response)
