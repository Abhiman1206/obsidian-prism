from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class TokenCipher:
    """Versioned token cipher with key-rotation support.

    Current format: v2:<key_id>:<fernet_ciphertext>
    Legacy format: base64-url XOR payload (kept for backward compatibility)
    """

    def __init__(self, secret: str | None = None) -> None:
        configured = secret or os.getenv("PROVIDER_TOKEN_SECRET") or "dev-provider-token-secret"
        self._key = hashlib.sha256(configured.encode("utf-8")).digest()
        self._legacy_key = self._key

        configured_keys = os.getenv("PROVIDER_TOKEN_KEYS", "")
        parsed = [entry.strip() for entry in configured_keys.split(",") if entry.strip()]

        if parsed:
            key_materials = parsed
        else:
            # Deterministic default for local development when no explicit keys are configured.
            key_materials = [
                base64.urlsafe_b64encode(hashlib.sha256(configured.encode("utf-8")).digest()).decode("ascii")
            ]

        fernets = [Fernet(key.encode("ascii")) for key in key_materials]
        self._current_fernet = fernets[0]
        self._multi_fernet = MultiFernet(fernets)
        self._current_key_id = hashlib.sha256(key_materials[0].encode("ascii")).hexdigest()[:12]

    def encrypt(self, plaintext: str) -> str:
        token = self._current_fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")
        return f"v2:{self._current_key_id}:{token}"

    def decrypt(self, ciphertext: str) -> str:
        if ciphertext.startswith("v2:"):
            parts = ciphertext.split(":", 2)
            if len(parts) != 3:
                raise ValueError("Invalid v2 token format")
            try:
                raw = self._multi_fernet.decrypt(parts[2].encode("ascii"))
            except InvalidToken as exc:
                raise ValueError("Unable to decrypt token with configured keys") from exc
            return raw.decode("utf-8")

        # Legacy fallback path.
        data = base64.urlsafe_b64decode(ciphertext.encode("ascii"))
        raw = bytes(data[i] ^ self._legacy_key[i % len(self._legacy_key)] for i in range(len(data)))
        return raw.decode("utf-8")

    def needs_rotation(self, ciphertext: str) -> bool:
        return not ciphertext.startswith(f"v2:{self._current_key_id}:")
