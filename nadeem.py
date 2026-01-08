# Full working script (fixed syntax errors and rich.Text usage).
# Requirements: pip install pycryptodome rich requests
import time
import io
import struct
import base64
import sys
import requests

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# --- ANIMATION UTILITY ---
def animate_text(text, color="green", style="bold", delay=0.01):
    """Typing animation effect using rich Console."""
    # Use Text style combining style and color so Text() doesn't receive unexpected 'color' kwarg
    combined_style = f"{style} {color}".strip()
    for char in text:
        console.print(Text(char, style=combined_style), end="")
        # flush to make animation appear immediately
        try:
            console.file.flush()
        except Exception:
            pass
        time.sleep(delay)
    console.print("")  # newline


def show_logo(delay_per_char=0.002):
    """Displays the NADEEM logo with animation."""
    logo = (
        "    ███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗\n"
        "    ████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║\n"
        "    ██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║\n"
        "    ██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║\n"
        "    ██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║\n"
        "    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝\n"
    )
    console.print(Panel(logo, style="bold green", title="[white]WELCOME[/white]"))
    animate_text(">>> SCRIPT LOADED SUCCESSFULLY...", color="green", delay=delay_per_char)
    console.print("-" * 50)


def display_token(token, color="green", style="bold", animate=True, delay=0.003):
    """Print token in color and add underline beneath it."""
    if animate:
        animate_text(token, color=color, style=style, delay=delay)
    else:
        console.print(Text(token, style=f"{style} {color}"))
    underline = "-" * max(10, len(token))
    console.print(Text(underline, style=f"{style} {color}"))
    console.print("")  # newline


# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except Exception:
    console.print("[red]Error: 'pycryptodome' module not found.[/red]")
    console.print("Run: pip install pycryptodome")
    raise SystemExit(1)


class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
        """
        Fetch public key from the endpoint. Returns (public_key_pem_str, key_id).
        This may fail if endpoint changes or requires different parameters.
        """
        try:
            url = "https://b-graph.facebook.com/pwd_key_fetch"
            params = {
                "version": "2",
                "flow": "CONTROLLER_INITIALIZATION",
                "method": "GET",
                "fb_api_req_friendly_name": "pwdKeyFetch",
                "fb_api_caller_class": "com.facebook.auth.login.AuthOperations",
                "access_token": "438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28",
            }
            resp = requests.post(url, params=params, timeout=10)
            resp.raise_for_status()
            j = resp.json()
            public_key = j.get("public_key")
            key_id = str(j.get("key_id", "25"))
            if not public_key:
                raise ValueError("No public_key in response")
            return public_key, key_id
        except Exception as e:
            raise Exception(f"Public key fetch error: {e}")

    @staticmethod
    def encrypt(password, public_key=None, key_id="25"):
        """
        Encrypt the given password using hybrid RSA + AES-GCM.
        Returns the Facebook-style encoded string.
        """
        if public_key is None:
            public_key, key_id = FacebookPasswordEncryptor.get_public_key()

        try:
            rand_key = get_random_bytes(32)
            iv = get_random_bytes(12)

            pubkey = RSA.import_key(public_key)
            cipher_rsa = PKCS1_v1_5.new(pubkey)
            encrypted_rand_key = cipher_rsa.encrypt(rand_key)

            cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
            current_time = int(time.time())
            cipher_aes.update(str(current_time).encode("utf-8"))
            encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))

            buf = io.BytesIO()
            buf.write(bytes([1, int(key_id) if str(key_id).isdigit() else 25]))
            buf.write(iv)
            buf.write(struct.pack("<h", len(encrypted_rand_key)))
            buf.write(encrypted_rand_key)
            buf.write(auth_tag)
            buf.write(encrypted_passwd)

            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"#PWD_FB4A:2:{current_time}:{encoded}"
        except Exception as e:
            raise Exception(f"Encryption error: {e}")


class FacebookAppTokens:
    APPS = {
        "FB_ANDROID": {"name": "Facebook For Android", "app_id": "350685531728"},
        "MESSENGER_ANDROID": {"name": "Facebook Messenger For Android", "app_id": "256002347743983"},
        "FB_LITE": {"name": "Facebook For Lite", "app_id": "275254692598279"},
        "MESSENGER_LITE": {"name": "Facebook Messenger For Lite", "app_id": "200424423651082"},
        "ADS_MANAGER_ANDROID": {"name": "Ads Manager App For Android", "app_id": "438142079694454"},
        "PAGES_MANAGER_ANDROID": {"name": "Pages Manager For Android", "app_id": "121876164619130"},
    }

    @staticmethod
    def get_app_id(app_key):
        app = FacebookAppTokens.APPS.get(app_key)
        return app["app_id"] if app else None

    @staticmethod
    def get_all_app_keys():
        return list(FacebookAppTokens.APPS.keys())

    @staticmethod
    def extract_token_prefix(token):
        for i, char in enumerate(token):
            if char.islower():
                return token[:i]
        return token


class FacebookLogin:
    API_URL = "https://b-graph.facebook.com/auth/login"
    ACCESS_TOKEN = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
    API_KEY = "882a8490361da98702bf97a021ddc14d"
    SIG = "214049b9f17c38bd767de53752b53946"

    BASE_HEADERS = {
        "content-type": "application/x-www-form-urlencoded",
        "x-fb-net-hni": "45201",
        "zero-rated": "0",
        "x-fb-sim-hni": "45201",
        "x-fb-connection-quality": "EXCELLENT",
        "x-fb-friendly-name": "authenticate",
        "x-fb-connection-bandwidth": "78032897",
        "x-tigon-is-retry": "False",
        "authorization": "OAuth null",
        "x-fb-connection-type": "WIFI",
        "x-fb-device-group": "3342",
        "priority": "u=3,i",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True",
    }

    def __init__(self, uid_phone_mail, password, machine_id=None, convert_token_to=None, convert_all_tokens=False):
        self.uid_phone_mail = uid_phone_mail

        # Accept already-encrypted password or plain; if plain, encrypt
        if isinstance(password, str) and password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            # encrypt may raise if public key fetch fails
            self.password = FacebookPasswordEncryptor.encrypt(password)

        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
        elif convert_token_to:
            self.convert_token_to = convert_token_to if isinstance(convert_token_to, list) else [convert_token_to]
        else:
            # default: no conversion requested
            self.convert_token_to = []

    def build_payload(self):
        """Build payload for a login attempt (placeholder)."""
        payload = {
            "api_key": self.API_KEY,
            "email": self.uid_phone_mail,
            "password": self.password,
            "format": "JSON",
        }
        return payload

    def login_request(self, timeout=10):
        """
        Performs a POST to the API_URL with built payload.
        This is provided as an optional helper. The API may require additional params/signing.
        """
        try:
            payload = self.build_payload()
            resp = requests.post(self.API_URL, data=payload, headers=self.BASE_HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Show animated logo and display tokens in green with underlines
    show_logo()
    animate_text(">>> STARTING NADEEM TOOL...", color="green")
    console.print("")

    console.print(Panel("Application Tokens", style="green"))
    for key in FacebookAppTokens.get_all_app_keys():
        app_id = FacebookAppTokens.get_app_id(key)
        display_token(f"{key}: {app_id}")

    console.print(Panel("Main Credentials", style="green"))
    display_token(f"ACCESS_TOKEN: {FacebookLogin.ACCESS_TOKEN}")
    display_token(f"API_KEY: {FacebookLogin.API_KEY}")
    display_token(f"SIG: {FacebookLogin.SIG}")

    animate_text(">>> READY", color="green")
