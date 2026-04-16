import adafruit_requests
import adafruit_connection_manager
import wifi
import gc

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
session = adafruit_requests.Session(pool, ssl_context)

class SendRequest:
    app_state = None

    @staticmethod
    def _cleanup():
        try:
            adafruit_connection_manager.connection_manager_close_all(pool)
        except Exception as e:
            print("[Cleanup] error: " + str(e))
        gc.collect()

    @staticmethod
    def post(webhook_url, payload = {}, headers = None):
        if SendRequest.app_state and not SendRequest.app_state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return None
        try:
            with session.post(webhook_url, json=payload, headers=headers) as response:
                data = response.json()
                print(data)
                return data
        except Exception as e:
            print("POST error: " + str(e))
            return None
        finally:
            SendRequest._cleanup()

    @staticmethod
    def post_sheets(url):
        if SendRequest.app_state and not SendRequest.app_state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return None
        try:
            print("[Sheets] POSTing to: " + url[:60])
            with session.post(url, json={}, headers={"Connection": "close"}) as response:
                status = response.status_code
                body = response.text
                print("[Sheets] status=" + str(status))
                print("[Sheets] body=" + str(body))
        except Exception as e:
            print("[Sheets] POST error: " + str(e))
        finally:
            SendRequest._cleanup()

    @staticmethod
    def get(url):
        if SendRequest.app_state and not SendRequest.app_state.get("wifi_connected", False):
            print("No WiFi - skipping network request")
            return None
        try:
            with session.get(url, headers={"Connection": "close"}) as response:
                data = response.json()
                print(data)
                return data
        except Exception as e:
            print("GET error: " + str(e))
            return None
        finally:
            SendRequest._cleanup()