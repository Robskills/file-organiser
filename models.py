from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class FileContext:
    """Represents a file discovered on the file system."""
    path: Path
    filename: str
    extension: str
    parent_folder: str
    file_hash: Optional[str] = None
    size_bytes: int = 0

@dataclass
class ClassificationResult:
    """The result of the inference engine."""
    domain: str
    theme: str
    confidence: float
    reason: List[str] = field(default_factory=list)

    @property
    def is_confident(self) -> bool:
        # Threshold defined in requirements
        return self.confidence >= 0.6

@dataclass
class ActionPlan:
    """A planned action for a file."""
    source: Path
    destination: Path
    action_type: str  # 'MOVE', 'TRASH', 'SKIP'
    reason: str