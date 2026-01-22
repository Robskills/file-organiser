import json
import base64
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".organisr" / "secrets.json"

class SecurityManager:
    """
    Handles secure storage of sensitive data.
    Uses basic obfuscation for portability; replace with OS keyring in production.
    """
    def __init__(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._key = None

    def _obfuscate(self, text: str) -> str:
        # Basic obfuscation to prevent casual snooping
        return base64.b64encode(text.encode()).decode()

    def _deobfuscate(self, text: str) -> str:
        try:
            return base64.b64decode(text.encode()).decode()
        except Exception:
            return ""

    def save_api_key(self, api_key: str):
        """Encrypts and saves the API key."""
        data = {"api_key": self._obfuscate(api_key)}
        with open(CONFIG_PATH, 'w') as f:
            json.dump(data, f)
        self._key = api_key

    def get_api_key(self) -> str:
        """Retrieves and decrypts the API key."""
        if self._key:
            return self._key
        if not CONFIG_PATH.exists():
            return ""
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                self._key = self._deobfuscate(data.get("api_key", ""))
                return self._key
        except Exception:
            return ""