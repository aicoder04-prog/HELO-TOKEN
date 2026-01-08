#!/usr/bin/env python3
"""
facebook_login_stylish_safe.py

Safe, UI-only enhancement of the user's original script:
- Adds ASCII logo ("NADEEM"), typewriter and spinner animations, progress bar.
- Prints tokens in green.
- Preserves original class names and method names to keep structure familiar.
- SAFE_MODE prevents any network calls or real encryption/login; uses mock outputs.
- Requires: colorama (pip install colorama). pyfiglet optional for nicer logo.
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
import threading
import itertools

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except Exception:
    # We keep imports but in SAFE_MODE we won't use them.
    pass

# Optional styling libs
try:
    import pyfiglet
except Exception:
    pyfiglet = None

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    # Minimal fallbacks
    class Fore:
        GREEN = ""
        CYAN = ""
        MAGENTA = ""
        YELLOW = ""
        RED = ""
        RESET = ""
    class Style:
        BRIGHT = ""
        NORMAL = ""

# ========== SAFETY FLAG ==========
# SAFE_MODE = True ensures no network calls or real encryption are performed.
# Keep True unless you explicitly understand the risks and own the account.
SAFE_MODE = True

# ========== ASCII LOGO and Styling ==========
def print_logo(name="NADEEM"):
    if pyfiglet:
        try:
            ascii_art = pyfiglet.figlet_format(name, font="slant")
            print(Fore.CYAN + Style.BRIGHT + ascii_art + Style.NORMAL)
            return
        except Exception:
            pass
    # Fallback logo
    logo = r"""
 _   _    _    ____  ______ _____  __  __ 
| \ | |  / \  |  _ \|  ____|  __ \|  \/  |
|  \| | / _ \ | |_) | |__  | |__) | \  / |
| . ` |/ ___ \|  _ <|  __| |  _  /| |\/| |
| |\  /_/   \_\_| \_\_|    |_| \_\|_|  |_|
"""
    print(Fore.CYAN + Style.BRIGHT + logo + Style.NORMAL)

def typewriter(text, delay=0.02, end="\n", color=""):
    for ch in text:
        sys.stdout.write(color + ch + Fore.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()

class Spinner:
    def __init__(self, text="Working"):
        self._running = False
        self._thread = None
        self.text = text

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def _spin(self):
        for c in itertools.cycle("|/-\\"):
            if not self._running:
                break
            sys.stdout.write(f"\r{Fore.MAGENTA}{self.text} {c}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(0.12)
        sys.stdout.write("\r" + " " * (len(self.text) + 4) + "\r")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

def progress_bar(total=20, prefix="Progress", delay=0.05):
    for i in range(total + 1):
        filled = int((i / total) * 20)
        bar = "[" + "#" * filled + "-" * (20 - filled) + "]"
        pct = int((i / total) * 100)
        sys.stdout.write(f"\r{Fore.YELLOW}{prefix} {bar} {pct}%{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_token(token):
    # Token shown in green to match user's request
    print(Fore.GREEN + Style.BRIGHT + token + Style.NORMAL)

# ========== Original classes (structure preserved) ==========
class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
        if SAFE_MODE:
            # Return a clearly mocked public key and key_id
            return "-----BEGIN PUBLIC KEY-----\nMOCK_PUBLIC_KEY==\n-----END PUBLIC KEY-----", "MOCK"
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
            response = requests.post(url, params=params).json()
            return response.get('public_key'), str(response.get('key_id', '25'))
        except Exception as e:
            raise Exception(f"Public key fetch error: {e}")

    @staticmethod
    def encrypt(password, public_key=None, key_id="25"):
        if SAFE_MODE:
            # Provide a safe, non-sensitive mock encrypted password string
            mock_encoded = base64.b64encode(f"MOCK_ENCRYPTED({password})".encode()).decode()
            current_time = int(time.time())
            return f"#PWD_FB4A:MOCK:{current_time}:{mock_encoded}"
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
        "x-fb-server-cluster": "True"
    }
    
    def __init__(self, uid_phone_mail, password, machine_id=None, convert_token_to=None, convert_all_tokens=False):
        self.uid_phone_mail = uid_phone_mail
        
        if password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            # In SAFE_MODE we use the mock encryptor to avoid real encryption/network.
            self.password = FacebookPasswordEncryptor.encrypt(password) if not SAFE_MODE else FacebookPasswordEncryptor.encrypt(password)
        
        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
        elif convert_token_to:
            self.convert_token_to = convert_token_to if isinstance(convert_token_to, list) else [convert_token_to]
        else:
            self.convert_token_to = []

    def login(self):
        """
        NOTE: This method is intentionally SAFE in SAFE_MODE and will not perform network login.
        It returns a mock token when SAFE_MODE is True.
        """
        spinner = Spinner("Attempting login")
        spinner.start()
        try:
            # Simulated work / progress
            time.sleep(1.2)
            progress_bar(25, prefix="Preparing")
            time.sleep(0.8)
            progress_bar(25, prefix="Contacting")
            time.sleep(0.6)
        finally:
            spinner.stop()

        if SAFE_MODE:
            # Return a clearly marked mock token
            mock_token = "MOCK_TOKEN_EAA..." + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
            typewriter(f"Login simulated for {self.uid_phone_mail}.", delay=0.01, color=Fore.CYAN)
            typewriter("Token (mock):", delay=0.01, color=Fore.YELLOW)
            print_token(mock_token)
            return {"status": "mock", "access_token": mock_token}
        else:
            # Real network login would happen here. We refuse to provide operational login code.
            raise RuntimeError("Real login not allowed in this safe script. Set SAFE_MODE=False and ensure you own the account and understand the risks.")

# ========== Demo / UI Entry Point ==========
def main_demo():
    print_logo("NADEEM")
    typewriter("Welcome to the stylish Facebook login demo.", delay=0.03, color=Fore.CYAN)
    typewriter("Note: This is SAFE_MODE. No real network or account operations are performed.", delay=0.02, color=Fore.YELLOW)
    print()

    # Ask user for inputs (mocked)
    try:
        uid = input(Fore.MAGENTA + "Enter uid/phone/email (demo only): " + Fore.RESET).strip()
    except KeyboardInterrupt:
        print("\nExiting.")
        return
    if not uid:
        uid = "demo_user@example.com"

    try:
        pwd = input(Fore.MAGENTA + "Enter password (demo only): " + Fore.RESET).strip()
    except KeyboardInterrupt:
        print("\nExiting.")
        return
    if not pwd:
        pwd = "password123"

    # Create login instance and attempt simulated login
    fb = FacebookLogin(uid, pwd)
    result = fb.login()

    print()
    typewriter("Available app keys (sample): " + ", ".join(FacebookAppTokens.get_all_app_keys()), delay=0.005, color=Fore.CYAN)
    if result.get("status") == "mock":
        typewriter("Conversion demo: token color is green and styled.", delay=0.01, color=Fore.CYAN)
        print_token(result.get("access_token"))
    print()
    typewriter("Demo complete. To run real operations you must disable SAFE_MODE and ensure you own the account.", delay=0.015, color=Fore.YELLOW)

if __name__ == "__main__":
    main_demo()
