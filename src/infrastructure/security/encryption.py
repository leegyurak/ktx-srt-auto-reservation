"""AES-256-CBC encryption utility using machine ID as encryption key"""
import hashlib
import platform
import subprocess
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class EncryptionService:
    """AES-256-CBC encryption service using machine-specific identifier as key"""

    @staticmethod
    def _get_machine_id() -> str:
        """
        Get a stable machine identifier based on the OS

        - macOS: Hardware UUID from system_profiler
        - Windows: MachineGuid from registry
        - Linux: /etc/machine-id

        Returns:
            A unique, stable identifier for this machine
        """
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                # Get Hardware UUID from system_profiler
                result = subprocess.run(
                    ["system_profiler", "SPHardwareDataType"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'Hardware UUID' in line or 'UUID' in line:
                        # Extract UUID from line like "Hardware UUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                        machine_id = line.split(':')[-1].strip()
                        if machine_id:
                            return machine_id

            elif system == "Windows":
                # Get MachineGuid from registry
                result = subprocess.run(
                    ["reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography", "/v", "MachineGuid"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'MachineGuid' in line:
                        # Extract GUID from registry output
                        machine_id = line.split()[-1].strip()
                        if machine_id:
                            return machine_id

            elif system == "Linux":
                # Read /etc/machine-id
                with open('/etc/machine-id', 'r') as f:
                    machine_id = f.read().strip()
                    if machine_id:
                        return machine_id

        except Exception as e:
            # If all else fails, fall back to a combination of system identifiers
            print(f"Warning: Could not get machine ID ({e}), using fallback method")
            pass

        # Fallback: use a combination of hostname and platform info
        import socket
        fallback_id = f"{socket.gethostname()}-{platform.node()}-{platform.machine()}"
        return fallback_id

    @staticmethod
    def _derive_key() -> bytes:
        """Derive a 256-bit key from the machine ID using SHA-256"""
        machine_id = EncryptionService._get_machine_id()
        # Use SHA-256 to derive a 32-byte (256-bit) key from machine ID
        key = hashlib.sha256(machine_id.encode('utf-8')).digest()
        return key

    @staticmethod
    def encrypt(plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-CBC

        Args:
            plaintext: The text to encrypt

        Returns:
            Base64-encoded string containing IV + ciphertext
        """
        if not plaintext:
            return ""

        key = EncryptionService._derive_key()

        # Generate a random 16-byte IV
        iv = get_random_bytes(AES.block_size)

        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad and encrypt
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)

        # Combine IV + ciphertext and encode to base64
        encrypted_data = iv + ciphertext
        return b64encode(encrypted_data).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_data: str) -> str | None:
        """
        Decrypt ciphertext using AES-256-CBC

        Args:
            encrypted_data: Base64-encoded string containing IV + ciphertext

        Returns:
            Decrypted plaintext or None if decryption fails
        """
        if not encrypted_data:
            return None

        try:
            key = EncryptionService._derive_key()

            # Decode from base64
            encrypted_bytes = b64decode(encrypted_data)

            # Extract IV and ciphertext
            iv = encrypted_bytes[:AES.block_size]
            ciphertext = encrypted_bytes[AES.block_size:]

            # Create cipher and decrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ciphertext)

            # Unpad and decode
            plaintext = unpad(padded_plaintext, AES.block_size)
            return plaintext.decode('utf-8')

        except Exception as e:
            # Decryption failed (wrong key, corrupted data, etc.)
            print(f"Decryption error: {e}")
            return None
