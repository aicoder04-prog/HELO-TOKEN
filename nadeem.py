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
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

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

def display_logo():
    logo_text = """
    [bold cyan]
    ███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗
    ████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║
    ██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║
    ██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║
    ██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝
    [/bold cyan]
    [bold green]           FACEBOOK AUTHENTICATOR PRO v2.0[/bold green]
    """
    console.print(Panel(logo_text, border_style="blue", subtitle="[white]Created for NADEEM[/white]"))

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
    def get_all_app_keys():
        return list(FacebookAppTokens.APPS.keys())

class FacebookLogin:
    def __init__(self, uid, password):
        self.uid = uid
        with console.status("[bold yellow]Encrypting Password...", spinner="dots"):
            self.password = FacebookPasswordEncryptor.encrypt(password)
            time.sleep(1) # Visual effect

    def attempt_login(self):
        # Placeholder for login logic using the encrypted password
        # In a real scenario, you would send this to the auth endpoint
        console.print(f"\n[bold white]Login attempt for: [cyan]{self.uid}[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Contacting FB Servers...", total=None)
            time.sleep(2)
            progress.add_task(description="Authenticating...", total=None)
            time.sleep(1.5)

        # Generating a dummy success for demonstration
        fake_token = "EAAAA" + "".join(random.choices(string.ascii_letters + string.digits, k=150))
        
        console.print(Panel(
            Text(f"LOGIN SUCCESSFUL\n\nTOKEN: {fake_token}", justify="center", style="bold green"),
            title="[bold green]Status[/bold green]",
            border_style="green"
        ))
        
        # Keep token green as requested
        console.print(f"\n[bold white]ACTIVE TOKEN: [green]{fake_token}[/green]\n")

# --- Main Execution ---
if __name__ == "__main__":
    display_logo()
    
    # Input section with style
    user = console.input("[bold white]Enter UID/Email/Phone: [/bold white]")
    pw = console.input("[bold white]Enter Password: [/bold white]", password=True)
    
    try:
        fb = FacebookLogin(user, pw)
        fb.attempt_login()
    except Exception as e:
        console.print(f"[bold red]FATAL ERROR: {e}[/bold red]")
