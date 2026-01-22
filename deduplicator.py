from pathlib import Path
from typing import Dict

from models import FileContext
from scanner import FileScanner

class Deduplicator:
    def __init__(self):
        # Maps hash -> original file path
        self.seen_hashes: Dict[str, Path] = {}

    def is_duplicate(self, context: FileContext) -> bool:
        """
        Checks if the file is a duplicate based on content hash.
        Calculates hash if not present in the context.
        """
        if not context.file_hash:
            # Calculate hash on demand using the Scanner's static method
            try:
                context.file_hash = FileScanner.calculate_hash(context.path)
            except OSError:
                return False

        if context.file_hash in self.seen_hashes:
            return True
        
        self.seen_hashes[context.file_hash] = context.path
        return False