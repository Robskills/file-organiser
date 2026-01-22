import os
import hashlib
from pathlib import Path
from typing import Generator
from models import FileContext
from taxonomy import IGNORED_DIRS, IGNORED_FILES

class FileScanner:
    def __init__(self, root_paths: list[Path]):
        self.root_paths = root_paths

    def scan(self) -> Generator[FileContext, None, None]:
        """Recursively scans directories and yields FileContext objects."""
        for root_path in self.root_paths:
            if not root_path.exists():
                continue

            for dirpath, dirnames, filenames in os.walk(root_path):
                # Modify dirnames in-place to skip ignored directories
                dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith('.')]
                
                for f in filenames:
                    if f in IGNORED_FILES or f.startswith('.'):
                        continue

                    full_path = Path(dirpath) / f
                    
                    # Skip symlinks to avoid loops
                    if full_path.is_symlink():
                        continue

                    try:
                        yield FileContext(
                            path=full_path,
                            filename=f,
                            extension=full_path.suffix,
                            parent_folder=Path(dirpath).name,
                            size_bytes=full_path.stat().st_size
                        )
                    except OSError:
                        # Permission errors or file vanished
                        continue

    @staticmethod
    def calculate_hash(path: Path, chunk_size: int = 8192) -> str:
        """Calculates SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()