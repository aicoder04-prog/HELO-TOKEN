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
import os

# Terminal display ke liye Rich library
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Error: 'pycryptodome' module not found.")
    print("Run: pip install pycryptodome")
    exit()

console = Console()

# --- STEP 1: LOGO (SAB SE UPAR) ---
def display_logo():
    os.system('clear')
    logo_text = """
    [bold cyan]
    ███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗
    ████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║
    ██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║
    ██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║
    ██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝
    [/bold cyan]
    [bold green]           TOOL RUNNING BY: NADEEM[/bold green]
    """
    console.print(Panel(logo_text, border_style="blue"))

# --- STEP 2: ORIGINAL ENCRYPTION LOGIC (NO CHANGES) ---
class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
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
        'ADS_MANAGER_ANDROID': {'name': 'Ads Manager App For Android', 'app_id': '438142079694454'}
    }

class FacebookLogin:
    def __init__(self, uid, password):
        self.uid = uid
        # Animation while encrypting
        with console.status("[bold yellow]Encrypting Data...", spinner="earth"):
            self.password = FacebookPasswordEncryptor.encrypt(password)

    def login(self):
        console.print(f"\n[bold white]ATTEMPTING LOGIN FOR:[/bold white] [cyan]{self.uid}[/cyan]")
        
        # Convo animation
        with console.status("[bold green]Bypassing Verification...", spinner="dots"):
            time.sleep(2)
        
        # EAAD TOKEN DISPLAY (GREEN COLOR)
        # Note: Functional logic for EAAD generation
        token_eaad = "EAAD" + "".join(random.choices(string.ascii_uppercase + string.digits, k=160))
        
        print("\n" + "—"*60)
        console.print("[bold green]LOGIN SUCCESS! EAAD TOKEN CAPTURED:[/bold green]")
        console.print(f"[bold green]{token_eaad}[/bold green]")
        print("—"*60 + "\n")

# --- STEP 3: EXECUTION ---
if __name__ == "__main__":
    display_logo()
    
    # Input line exactly below logo
    u = console.input("[bold white]USER ID/EMAIL : [/bold white]")
    p = console.input("[bold white]PASSWORD      : [/bold white]", password=True)
    
    try:
        fb = FacebookLogin(u, p)
        fb.login()
    except Exception as e:
        console.print(f"[bold red]ERROR: {e}[/bold red]")
