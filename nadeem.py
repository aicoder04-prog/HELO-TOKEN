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

console = Console()

# --- ANIMATION UTILITY ---
def animate_text(text, color="green", style="bold"):
    """Creates a typing animation effect."""
    for char in text:
        sys.stdout.write(f"[{color}]{char}[/{color}]" if "[" in text else char)
        console.print(Text(char, style=style, color=color), end="")
        sys.stdout.flush()
        time.sleep(0.01)
    print()

def show_logo():
    """Displays the NADEEM logo with animation."""
    logo = """
    ███╗   ██╗ █████╗ ██████╗ ███████╗███████╗███╗   ███╗
    ████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝████╗ ████║
    ██╔██╗ ██║███████║██║  ██║█████╗  █████╗  ██╔████╔██║
    ██║╚██╗██║██╔══██║██║  ██║██╔══╝  ██╔══╝  ██║╚██╔╝██║
    ██║ ╚████║██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝
    """
    console.print(Panel(logo, style="bold green", title="[WHITE]WELCOME[/WHITE]"))
    animate_text(">>> SCRIPT LOADED SUCCESSFULLY...", color="green")
    print("-" * 50)

# Crypto libraries check
try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
except ImportError:
    console.print("[red]Error: 'pycryptodome' module not found.[/red]")
    print("Run: pip install pycryptodome")
    exit()

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
    # (Existing constants kept identical)
    API_URL = "https://b-graph.facebook.com/auth/login"
    
    def __init__(self, uid_phone_mail, password, convert_all_tokens=True):
        show_logo() # Display logo on startup
        
        self.uid_phone_mail = uid_phone_mail
        animate_text(f"[*] Encrypting password for: {uid_phone_mail}...", "green")
        
        if password.startswith("#PWD_FB4A"):
            self.password = password
        else:
            self.password = FacebookPasswordEncryptor.encrypt(password)
        
        if convert_all_tokens:
            self.convert_token_to = FacebookAppTokens.get_all_app_keys()
            
        self.display_tokens()

    def display_tokens(self):
        """Displays tokens in green with an underlined divider."""
        animate_text("\n[bold green]GENERATED TOKENS:[/bold green]", "green")
        print("=" * 30) # Line below the title
        
        for key in self.convert_token_to:
            token_info = FacebookAppTokens.APPS[key]
            # Animation for each token line
            animate_text(f"[+] {token_info['name']}: {token_info['app_id']}", "green")
            
        print("-" * 50) # Final line below all tokens
        animate_text("PROCESS COMPLETED SUCCESSFULLY", "green")

# Example usage:
if __name__ == "__main__":
    # You can replace these with your actual login logic
    try:
        FacebookLogin("example_user", "example_pass")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
