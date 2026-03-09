"""SSHKeyAccessor — ssh-keygen subprocess, key file management.

Pure I/O translation: wraps subprocess calls to ssh-keygen
and checks for key files on disk.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class SSHKeyAccessor:
    """Concrete implementation of ISSHKeyAccessor."""

    def __init__(self, ssh_dir: Path | None = None):
        """Initialize with optional custom SSH directory.

        Args:
            ssh_dir: Path to .ssh directory. Defaults to ~/.ssh.
        """
        self._ssh_dir = ssh_dir or Path.home() / ".ssh"

    def generate_key(self, key_type: str = "ed25519", comment: str = "") -> Path:
        """Generate an SSH key pair.

        Args:
            key_type: Key algorithm (e.g. "ed25519", "rsa").
            comment: Comment for the key (typically an email address).

        Returns:
            Path to the generated private key file.

        Raises:
            subprocess.CalledProcessError: If ssh-keygen fails.
            FileNotFoundError: If ssh-keygen is not installed.
        """
        self._ssh_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        key_path = self._ssh_dir / f"id_{key_type}"

        cmd = ["ssh-keygen", "-t", key_type, "-f", str(key_path), "-N", ""]
        if comment:
            cmd.extend(["-C", comment])

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise FileNotFoundError("ssh-keygen is not installed or not on PATH")

        return key_path

    def key_exists(self) -> bool:
        """Check whether an SSH key already exists.

        Checks for id_ed25519, id_rsa, and id_ecdsa in the SSH directory.

        Returns:
            True if any standard key file exists.
        """
        key_names = ["id_ed25519", "id_rsa", "id_ecdsa"]
        return any((self._ssh_dir / name).exists() for name in key_names)
