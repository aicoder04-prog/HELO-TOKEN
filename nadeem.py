#!/usr/bin/env python3
"""
facebook_oauth_nadeem.py

Safe, legitimate Facebook OAuth example:
- Opens the Facebook OAuth dialog (user logs in interactively in the browser)
- Receives the callback and exchanges the code for a short-lived access token
- Optionally exchanges for a long-lived token using the App Secret
- Displays token in green and a NADEEM header

Configure:
- Set CLIENT_ID and CLIENT_SECRET (from developers.facebook.com)
- Add the redirect URI (e.g. http://localhost:5000/callback) to your app's OAuth redirect URIs
- Run: python facebook_oauth_nadeem.py
"""

import os
import secrets
import webbrowser
from urllib.parse import urlencode

from flask import Flask, redirect, request, render_template_string
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ----- CONFIG -----
CLIENT_ID = os.environ.get("FB_CLIENT_ID", "<REPLACE_WITH_YOUR_APP_ID>")
CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET", "<REPLACE_WITH_YOUR_APP_SECRET>")
# Must match the Redirect URI set in your Facebook app settings
REDIRECT_URI = os.environ.get("FB_REDIRECT_URI", "http://localhost:5000/callback")

# Requested scopes - choose what your app needs and what Facebook approves
SCOPES = ["email", "public_profile"]

# Facebook Graph versions
FB_OAUTH_DIALOG = "https://www.facebook.com/v16.0/dialog/oauth"
FB_TOKEN_EXCHANGE = "https://graph.facebook.com/v16.0/oauth/access_token"

app = Flask(__name__)
console = Console()

# Simple NADEEM ascii logo (for console output)
NADEEM_LOGO = r"""
 _   _    _    ____  _____  _____  __  __ 
| \ | |  / \  |  _ \| ____||  ___||  \/  |
|  \| | / _ \ | | | |  _|  | |_   | |\/| |
| |\  |/ ___ \| |_| | |___ |  _|  | |  | |
|_| \_/_/   \_\____/|_____||_|    |_|  |_|
"""

# HTML template for callback result
RESULT_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>NADEEM - Facebook OAuth Result</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f1724; color:#d1d5db; text-align:center; padding:30px; }
    .panel { display:inline-block; text-align:left; background:#071029; padding:18px 24px; border-radius:10px; box-shadow:0 6px 18px rgba(0,0,0,0.5); }
    .logo { font-family: monospace; color: #7dd3fc; white-space: pre; text-align:center; margin-bottom:8px; }
    .token { color: #3ad62c; word-break:break-all; font-family:monospace; background:#02140b; padding:8px; border-radius:6px; }
    .small { color:#9ca3af; font-size:0.9rem; margin-top:8px; }
    a { color:#60a5fa; text-decoration:none; }
  </style>
</head>
<body>
  <div class="panel">
    <div class="logo">{{ logo }}</div>
    <h2>Facebook OAuth Complete</h2>
    {% if error %}
      <div style="color:#f87171;">Error: {{ error }}</div>
    {% else %}
      <div><strong>Short-lived access token:</strong></div>
      <div class="token">{{ access_token }}</div>
      {% if long_token %}
        <div style="margin-top:10px;"><strong>Long-lived token:</strong></div>
        <div class="token">{{ long_token }}</div>
      {% endif %}
      <div class="small">Keep tokens secret. This page is displayed locally only.</div>
    {% endif %}
    <div style="margin-top:12px;"><a href="/">Start over</a></div>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    # Create a link to start the OAuth flow
    state = secrets.token_urlsafe(16)
    # We'll store state client-side in the URL (and validate on callback for CSRF)
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": ",".join(SCOPES),
        "response_type": "code",
    }
    oauth_url = FB_OAUTH_DIALOG + "?" + urlencode(params)
    html = f"""
    <!doctype html>
    <html>
    <head><meta charset="utf-8"><title>NADEEM Facebook OAuth Demo</title></head>
    <body style="font-family:Arial; background:#071026; color:#e6eef8; text-align:center; padding:40px;">
      <pre style="color:#7dd3fc; font-family:monospace;">{NADEEM_LOGO}</pre>
      <h2>NADEEM — Facebook OAuth demo</h2>
      <p>Click the button below to open Facebook's login/consent dialog. You will log in interactively in the browser.</p>
      <p><a href="{oauth_url}" style="background:#2563eb; color:white; padding:10px 18px; border-radius:6px; text-decoration:none;">Start Facebook OAuth</a></p>
      <p style="color:#94a3b8;">Redirect URI: {REDIRECT_URI}</p>
    </body>
    </html>
    """
    return html

@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return render_template_string(RESULT_PAGE, logo=NADEEM_LOGO, error=error, access_token=None, long_token=None)

    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return render_template_string(RESULT_PAGE, logo=NADEEM_LOGO, error="Missing code in callback", access_token=None, long_token=None)

    # Exchange the authorization code for a short-lived access token
    try:
        token_params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "client_secret": CLIENT_SECRET,
            "code": code
        }
        resp = requests.get(FB_TOKEN_EXCHANGE, params=token_params, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
        short_lived_token = token_data.get("access_token")
    except Exception as e:
        return render_template_string(RESULT_PAGE, logo=NADEEM_LOGO, error=f"Token exchange error: {e}", access_token=None, long_token=None)

    long_token = None
    # Optionally exchange for a long-lived token (server-side)
    try:
        exchange_params = {
            "grant_type": "fb_exchange_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "fb_exchange_token": short_lived_token
        }
        long_resp = requests.get(FB_TOKEN_EXCHANGE, params=exchange_params, timeout=10)
        long_resp.raise_for_status()
        long_data = long_resp.json()
        long_token = long_data.get("access_token")
    except Exception:
        # It's fine if this fails (not all apps or tokens convert); we continue.
        long_token = None

    # Console output (NADEEM styling) - token shown in green
    console.print(Panel(Text("NADEEM — Facebook OAuth result", justify="center"), style="bold blue"))
    console.print(NADEEM_LOGO, style="cyan")
    console.print("Short-lived token:", style="bold")
    console.print(short_lived_token or "<none>", style="bold green")
    if long_token:
        console.print("Long-lived token:", style="bold")
        console.print(long_token, style="bold green")

    return render_template_string(RESULT_PAGE, logo=NADEEM_LOGO, error=None, access_token=short_lived_token, long_token=long_token)

if __name__ == "__main__":
    if CLIENT_ID.startswith("<REPLACE") or CLIENT_SECRET.startswith("<REPLACE"):
        console.print("[bold red]ERROR:[/bold red] Set FB_CLIENT_ID and FB_CLIENT_SECRET environment variables or edit this file.", style="bold")
        console.print("Example export commands (Linux/Mac):")
        console.print("  export FB_CLIENT_ID=your_app_id")
        console.print("  export FB_CLIENT_SECRET=your_app_secret")
        console.print("Make sure the redirect URI is configured in the Facebook app settings.")
    else:
        console.print(Panel(Text("NADEEM Facebook OAuth demo starting (open http://localhost:5000)", justify="center"), style="bold magenta"))
        webbrowser.open("http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
