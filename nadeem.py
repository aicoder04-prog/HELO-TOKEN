#!/usr/bin/env python3
"""
facebook_login_with_animation.py

Safe demo wrapper around the provided code:
- Adds terminal animations and styling (using rich)
- Adds "NADEEM" logo and name
- Shows tokens in green color in the conversation output
- Keeps class structure similar to your original script
- Runs in demo_mode=True by default to avoid calling live Facebook endpoints

Dependencies:
    pip install rich pycryptodome requests
"""

import random
import string
import json
import time
import requests
import uuid
import base64
import io
import struct
import sys
from typing import Optional, List

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Error: 'pycryptodome' module not found.")
    print("Run: pip install pycryptodome")
    exit()

# Rich for animations and color
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
except ImportError:
    print("Error: 'rich' module not found.")
    print("Run: pip install rich")
    exit()

console = Console()

class FacebookPasswordEncryptor:
    """
    Encryption helper.
    NOTE: For safety, get_public_key() is not called automatically in demo mode.
    If you supply a real public_key (and set demo_mode=False at runtime), the original encryption
    will run. By default demo safe simulated encryption is used.
    """
    @staticmethod
    def get_public_key(demo_mode=True):
        if demo_mode:
            # Return a dummy RSA public key for demo (PEM) — not used for real login
            dummy_key = RSA.generate(1024).publickey().export_key().decode()
            return dummy_key, "25"
        try:
            url = 'https://b-graph.facebook.com/pwd_key_fetch'
            params = {
                'version': '2',
                'flow': 'CONTROLLER_INITIALIZATION',
                'method': 'GET',
                'fb_api_req_friendly_name': 'pwdKeyFetch',
                'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
                'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
            }
            response = requests.post(url, params=params, timeout=10).json()
            return response.get('public_key'), str(response.get('key_id', '25'))
        except Exception as e:
            raise Exception(f"Public key fetch error: {e}")

    @staticmethod
    def encrypt(password: str, public_key: Optional[str]=None, key_id: str="25", demo_mode: bool=True) -> str:
        """
        If demo_mode=True then we create a deterministic, safe simulated encrypted string.
        If demo_mode=False and a public_key is available, run the real encryption (kept compatible).
        """
        if demo_mode:
            # Simulated, reversible-for-demo token (not real encryption)
            now = int(time.time())
            payload = f"demo::{now}::{base64.b64encode(password.encode()).decode()}"
            encoded = base64.b64encode(payload.encode()).decode()
            return f"#PWD_FB4A:DEMO:{now}:{encoded}"
        # Real encryption path (use with caution)
        if public_key is None:
            public_key, key_id = FacebookPasswordEncryptor.get_public_key(demo_mode=False)
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
            buf.write(bytes([1, int(key_id)]))
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
        'FB_ANDROID': {'name': 'Facebook For Android', 'app_id': '350685531728'},
        'MESSENGER_ANDROID': {'name': 'Facebook Messenger For Android', 'app_id': '256002347743983'},
        'FB_LITE': {'name': 'Facebook For Lite', 'app_id': '275254692598279'},
        'MESSENGER_LITE': {'name': 'Facebook Messenger For Lite', 'app_id': '200424423651082'},
        'ADS_MANAGER_ANDROID': {'name': 'Ads Manager App For Android', 'app_id': '438142079694454'},
        'PAGES_MANAGER_ANDROID': {'name': 'Pages Manager For Android', 'app_id': '121876164619130'}
    }

    @staticmethod
    def get_app_id(app_key):
        app = FacebookAppTokens.APPS.get(app_key)
        return app['app_id'] if app else None

    @staticmethod
    def get_all_app_keys():
        return list(FacebookAppTokens.APPS.keys())

    @staticmethod
    def extract_token_prefix(token: str) -> str:
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
        "x-fb-server-cluster": "True"
    }

    def __init__(
        self,
        uid_phone_mail: str,
        password: str,
        machine_id: Optional[str]=None,
        convert_token_to: Optional[List[str]]=None,
        convert_all_tokens: bool=False,
        demo_mode: bool=True
    ):
        self.uid_phone_mail = uid_phone_mail
        self.demo_mode = demo_mode

        # If password already looks encrypted, keep as-is; else encrypt (demo or real depending on demo_mode)
        if password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            self.password = FacebookPasswordEncryptor.encrypt(password, demo_mode=self.demo_mode)

        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
        elif convert_token_to:
            self.convert_token_to = convert_token_to if isinstance(convert_token_to, list) else [convert_token_to]
        else:
            self.convert_token_to = []

        self.machine_id = machine_id or str(uuid.uuid4())

    def simulate_login(self):
        """Simulated login flow for demo purposes. Returns a fake access token."""
        # Simulate network and processing time using progress bar animation
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            t_encrypt = progress.add_task("[cyan]Encrypting password...", total=None)
            time.sleep(0.8 + random.random() * 0.8)
            progress.remove_task(t_encrypt)

            t_login = progress.add_task("[magenta]Contacting server (simulated)...", total=None)
            time.sleep(1.0 + random.random() * 1.2)
            progress.remove_task(t_login)

        # Create a deterministic fake token so output is repeatable per uid
        seed = (self.uid_phone_mail + self.password)[:32].encode()
        rnd = base64.b64encode(seed).decode('utf-8').replace('=', '')[:32]
        fake_token = f"EAA{rnd}0|{self.machine_id[:6]}"
        return fake_token

    def real_login(self):
        """
        Placeholder for how a real login would be implemented.
        Not executed in demo mode. Kept for structural parity with original script.
        """
        raise NotImplementedError("Real login is disabled in this demo script for safety.")

    def login(self):
        if self.demo_mode:
            return self.simulate_login()
        else:
            # If someone sets demo_mode=False, they must implement the real call themselves.
            # We intentionally do not perform real Facebook login here.
            return self.real_login()

    def convert_token(self, token: str, target_app_key: str) -> str:
        """
        Simulate converting/exchanging token for a different app id. In real life this requires API calls.
        We just craft a token-like string and keep the colour display in the UI.
        """
        app_id = FacebookAppTokens.get_app_id(target_app_key) or "UNKNOWN_APP"
        return f"{token}.{app_id}.{target_app_key}"


# ----- UI helpers (animations & styling) -----
def print_na_deem_logo():
    # Animated ASCII "NADEEM" logo using gradient and center alignment
    logo_lines = [
        r" _   _    _    ____  _____  _____  __  __ ",
        r"| \ | |  / \  |  _ \| ____||  ___||  \/  |",
        r"|  \| | / _ \ | | | |  _|  | |_   | |\/| |",
        r"| |\  |/ ___ \| |_| | |___ |  _|  | |  | |",
        r"|_| \_/_/   \_\____/|_____||_|    |_|  |_|",
    ]
    colors = ["bold magenta", "bold blue", "bold cyan", "bold green", "bold yellow"]
    with Live(console=console, refresh_per_second=8, transient=True) as live:
        for i in range(8):
            txt = Text()
            for idx, line in enumerate(logo_lines):
                style = colors[(i + idx) % len(colors)]
                txt.append(line + "\n", style=style)
            txt = Align.center(txt)
            panel = Panel(txt, subtitle="[bold white]by NADEEM", padding=(1, 4))
            live.update(panel)
            time.sleep(0.15)

def typewriter_print(text: str, delay: float=0.025, style: Optional[str]=None):
    """Typewriter effect printing."""
    for ch in text:
        if style:
            console.print(ch, end="", style=style, highlight=False, soft_wrap=True)
        else:
            console.print(ch, end="", highlight=False, soft_wrap=True)
        time.sleep(delay)
    console.print()  # newline

def show_conversation(uid: str, token: str, converted_tokens: Optional[List[str]] = None):
    """Show a mock 'conversation' output with token in green."""
    console.rule("[bold green]Conversation")
    # Simulate chatting lines with typewriter
    typewriter_print(f"System: Welcome back, [bold]{uid}[/bold].", delay=0.01)
    typewriter_print(f"System: Your session token is:", delay=0.01)
    # Token in green
    console.print(f"[bold green]{token}[/bold green]")
    if converted_tokens:
        console.print()
        console.print("[bold]Converted Tokens:[/bold]")
        for ct in converted_tokens:
            console.print(f"[green]{ct}[/green]")

def main():
    console.clear()
    print_na_deem_logo()

    console.print(Panel("Stylish Facebook Login Demo — NADEEM", style="bold white on blue"))

    # Interactive prompt
    uid = console.input("[bold cyan]Enter UID / phone / email:[/bold cyan] ").strip()
    pwd = console.input("[bold cyan]Enter password (will be encrypted in demo):[/bold cyan] ", password=True).strip()

    # Demo mode by default for safety
    demo_mode = True
    console.print()
    typewriter_print("Starting login flow (demo-mode active). No real network login will be performed.", delay=0.01, style="italic dim")

    # optional: choose conversion targets
    conv_choice = console.input("Convert token to specific app keys? (comma-separated keys or leave blank for none) ").strip()
    conv_list = [c.strip() for c in conv_choice.split(",")] if conv_choice else []

    # instantiate and login
    fl = FacebookLogin(uid, pwd, convert_token_to=conv_list or None, demo_mode=demo_mode)

    # show animated progress for the whole flow
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=None),
        "{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console
    ) as progress:
        t = progress.add_task("[green]Running demo flow...", total=100)
        for i in range(10):
            time.sleep(0.12)
            progress.update(t, advance=10)

    token = fl.login()

    # Optionally simulate token conversions
    converted = []
    for target in fl.convert_token_to:
        converted.append(fl.convert_token(token, target))

    # Display conversation (with green token)
    show_conversation(uid, token, converted_tokens=converted if converted else None)

    console.print()
    console.print(Panel(Text("Thank you for using the stylish demo — NADEEM", justify="center"), style="bold magenta"))
    console.print("[dim]Note: This was a safe demo. To implement real network calls you must change demo_mode=False and provide proper API handling.[/dim]")

if __name__ == "__main__":
    main()
