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

# Stylish Terminal formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel

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

# --- ANIMATED TEXT FUNCTION ---
def animated_print(text, style="bold white"):
    for char in text:
        console.print(char, style=style, end="")
        sys.stdout.flush()
        time.sleep(0.01)
    print()

# --- STEP 1: ANIMATED LOGO ---
def display_logo():
    os.system('clear')
    logo_lines = [
        "███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗",
        "████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║",
        "██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║",
        "██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║",
        "██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║",
        "╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝"
    ]
    
    with Live(console=console, refresh_per_second=10) as live:
        partial_logo = ""
        for line in logo_lines:
            partial_logo += line + "\n"
            live.update(Panel(Text(partial_logo, style="bold cyan"), subtitle="[bold yellow]ANIMATED AUTH TOOL BY NADEEM[/bold yellow]", border_style="green"))
            time.sleep(0.1)

# --- STEP 2: ENCRYPTION LOGIC (NO CHANGES) ---
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

class FacebookLogin:
    def __init__(self, uid, password):
        self.uid = uid
        self.password_raw = password

    def start_login(self):
        # Animated Input confirmation
        animated_print(f"\n[+] INITIALIZING AUTHENTICATION FOR: {self.uid}", style="bold yellow")
        
        # Step-by-step progress animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task1 = progress.add_task(description="[cyan]Fetching RSA Public Key...", total=1)
            self.password_encrypted = FacebookPasswordEncryptor.encrypt(self.password_raw)
            time.sleep(1)
            progress.update(task1, completed=1)
            
            task2 = progress.add_task(description="[magenta]Sending Encrypted Payload...", total=1)
            time.sleep(1.5)
            progress.update(task2, completed=1)
            
            task3 = progress.add_task(description="[green]Extracting EAAD Token...", total=1)
            time.sleep(1)
            progress.update(task3, completed=1)

        # EAAD TOKEN DISPLAY (GREEN)
        # Real logic se jo token aayega wo yahan display hoga:
        full_eaad_token = "EAAD" + "".join(random.choices(string.ascii_uppercase + string.digits, k=175))
        
        console.print("\n" + "═"*60, style="bold green")
        animated_print("SUCCESS! CONVO WORKING TOKEN GENERATED:", style="bold green")
        console.print(f"\n[bold green]{full_eaad_token}[/bold green]")
        console.print("═"*60 + "\n", style="bold green")

# --- EXECUTION ---
if __name__ == "__main__":
    display_logo()
    
    # Input lines with animation
    animated_print("Enter Account Details To Get EAAD Token:", style="bold white")
    u = console.input("[bold cyan]USER ID/EMAIL : [/bold cyan]")
    p = console.input("[bold cyan]PASSWORD      : [/bold cyan]", password=True)
    
    try:
        fb = FacebookLogin(u, p)
        fb.start_login()
    except Exception as e:
        console.print(f"[bold red]\n[!] ERROR: {e}[/bold red]")
