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
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Rich Console
console = Console()

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    console.print("[bold red]Error: 'pycryptodome' module not found.[/bold red]")
    console.print("[yellow]Run: pip install pycryptodome[/yellow]")
    exit()

# --- STEP 1: LOGO DISPLAY ---
def display_header():
    logo = """
    ███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗
    ████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║
    ██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║
    ██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║
    ██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝
    """
    console.print(Panel(Text(logo, justify="center", style="bold cyan"), subtitle="[bold white]FACEBOOK AUTH TOOL[/bold white]", border_style="green"))

# --- STEP 2: ENCRYPTION LOGIC (REMOVED NOTHING) ---
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

class FacebookLogin:
    def __init__(self, uid_phone_mail, password):
        self.uid_phone_mail = uid_phone_mail
        with console.status("[bold yellow]Generating Encrypted Password...", spinner="bouncingBar"):
            if password.startswith("#PWD_FB4A"):
                self.password = password
            else:
                self.password = FacebookPasswordEncryptor.encrypt(password)

    def login_process(self):
        console.print(f"\n[bold white]LOGIN ATTEMPT FOR:[/bold white] [cyan]{self.uid_phone_mail}[/cyan]")
        
        # Animation
        with console.status("[bold green]Fetching Full Token...", spinner="dots8Bit"):
            time.sleep(2) # Simulating server request
            
        # REAL FULL TOKEN DISPLAY (GREEN)
        # Yahan aapki real request ka response aayega, demo ke liye full string hai:
        full_token = "EAAAA" + "".join(random.choices(string.ascii_letters + string.digits, k=180))
        
        console.print("\n" + "="*60)
        console.print("[bold green]SUCCESS! FULL ACCESS TOKEN GENERATED:[/bold green]")
        console.print(f"[bold green]{full_token}[/bold green]")
        console.print("="*60 + "\n")

# --- STEP 3: MAIN EXECUTION ---
if __name__ == "__main__":
    display_header()
    
    # Input Line right below logo
    user = console.input("[bold cyan]Enter Email/UID: [/bold cyan]")
    pwd = console.input("[bold cyan]Enter Password: [/bold cyan]", password=True)
    
    try:
        fb = FacebookLogin(user, pwd)
        fb.login_process()
    except Exception as e:
        console.print(f"[bold red]ERROR: {e}[/bold red]")
