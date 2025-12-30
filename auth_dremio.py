import os
import secrets
import threading
import webbrowser
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
DREMIO_CLIENT_ID = os.getenv("DREMIO_CLIENT_ID")
REDIRECT_URI = "http://localhost:8000/callback"
AUTH_URL = "https://app.dremio.cloud/oauth/authorize"
TOKEN_URL = "https://login.dremio.cloud/oauth/token"

# Global state to hold the token
auth_result = {}

@app.route("/")
def home():
    return "Dremio OAuth Helper is running. Close this window and check your terminal."

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code received.", 400

    # Exchange code for token
    try:
        response = requests.post(TOKEN_URL, json={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": DREMIO_CLIENT_ID
        })
        response.raise_for_status()
        data = response.json()
        
        access_token = data.get("access_token")
        auth_result["token"] = access_token
        
        return f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: green;">Authentication Successful!</h1>
                <p>You can close this window now.</p>
                <p>Your token has been captured by the script.</p>
            </body>
        </html>
        """
    except Exception as e:
        return f"Error exchanging token: {e}", 500

def run_server():
    app.run(port=8000)

def main():
    if not DREMIO_CLIENT_ID:
        print("❌ Error: DREMIO_CLIENT_ID is missing from .env")
        print("Please add DREMIO_CLIENT_ID=<your-client-id> to your .env file.")
        return

    print("🚀 Starting Dremio OAuth Flow...")
    
    # Generate Authorization URL
    # Note: Dremio might require 'state' or 'code_challenge' in stricter flows, 
    # but the simple flow often works with just response_type and client_id.
    auth_link = f"{AUTH_URL}?response_type=code&client_id={DREMIO_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    
    print(f"\n👉 Please visit this URL to login:\n{auth_link}\n")
    
    # Try to open browser automatically
    webbrowser.open(auth_link)

    # Start Flask server in a separate thread to handle the callback
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Waiting for callback on http://localhost:8000/callback...")
    
    # Simple polling or wait mechanism could go here, 
    # but for a CLI script we might just keep the main thread alive until we get the token.
    # Since app.run() block in the thread, we can monitor the global var.
    
    import time
    while "token" not in auth_result:
        time.sleep(1)
    
    token = auth_result["token"]
    print("\n✅ Authentication Successful!")
    print(f"\nAccess Token: {token}")
    print("\n📝 Add this to your .env file:")
    print(f"DREMIO_TOKEN={token}")
    
    # Optional: Append to .env automatically? 
    # Let's keep it safe and just print it for now, or ask user.
    # For simplicity in this interaction, we just print it.

if __name__ == "__main__":
    main()
