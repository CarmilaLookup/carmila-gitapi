"""
API Vercel - Validation de licences
Fichier : api/index.py

Deploiement gratuit sur vercel.com :
  1. Cree un compte sur vercel.com (gratuit)
  2. Importe ce repo GitHub sur Vercel
  3. Ajoute la variable d'environnement GITHUB_KEYS_URL dans les settings Vercel
"""

from http.server import BaseHTTPRequestHandler
import json, urllib.request, os
from datetime import datetime, timezone


GITHUB_KEYS_URL = os.environ.get("GITHUB_KEYS_URL", "")


def fetch_keys() -> dict:
    try:
        req = urllib.request.Request(
            GITHUB_KEYS_URL,
            headers={"Cache-Control": "no-cache", "User-Agent": "LicenseAPI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def validate(key: str, hwid: str) -> dict:
    keys = fetch_keys()

    if key not in keys:
        return {"status": "invalid", "message": "Cle introuvable.", "expires": ""}

    entry = keys[key]
    expires = entry.get("expires", "")

    # Verification expiration
    if expires and today() > expires:
        return {"status": "expired", "message": "Licence expiree.", "expires": expires}

    # Verification HWID
    stored_hwid = entry.get("hwid")
    if stored_hwid is None:
        # Premiere utilisation : on ne bloque pas (le HWID se lie cote client)
        pass
    elif stored_hwid != hwid:
        return {"status": "hwid_mismatch", "message": "Cle deja utilisee sur un autre PC.", "expires": expires}

    return {"status": "valid", "message": "Licence valide.", "expires": expires}


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        key  = body.get("key", "").strip()
        hwid = body.get("hwid", "unknown")

        result = validate(key, hwid)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, *args):
        pass  # Desactive les logs inutiles
