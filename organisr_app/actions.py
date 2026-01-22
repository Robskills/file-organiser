import shutil
import logging
from pathlib import Path
from datetime import datetime
import re
from models import ActionPlan

logger = logging.getLogger(__name__)

class ActionExecutor:
    def __init__(self, root_destination: Path, dry_run: bool = True):
        self.root_destination = root_destination
        self.dry_run = dry_run
        self.trash_dir = root_destination / ".trash" / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.created_folders = set()
        self.moved_files = []

    def execute(self, plan: ActionPlan):
        if plan.action_type == 'SKIP':
            logger.info(f"[SKIP] {plan.source} -> {plan.reason}")
            return

        if plan.action_type == 'TRASH':
            target_dir = self.trash_dir
            target_path = target_dir / plan.source.name
        else:
            # MOVE
            target_dir = plan.destination.parent
            target_path = plan.destination

        # Logging
        prefix = "[DRY-RUN]" if self.dry_run else "[EXECUTE]"
        logger.info(f"{prefix} {plan.action_type}: '{plan.source}' -> '{target_path}' ({plan.reason})")

        if not self.dry_run:
            self._perform_move(plan.source, target_dir, target_path)

    def _perform_move(self, source: Path, target_dir: Path, target_path: Path):
        try:
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                self.created_folders.add(str(target_dir))
            
            final_path = self._resolve_collision(target_path)
            
            shutil.move(str(source), str(final_path))
            self.moved_files.append((str(source), str(final_path)))
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")

    def _resolve_collision(self, target_path: Path) -> Path:
        """
        If file exists, append a counter: file.txt -> file_1.txt
        """
        if not target_path.exists():
            return target_path

        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _smart_rename(self, filename: str) -> str:
        """
        Renames file to a more suitable format for organization.
        Removes 'Copy of', '(1)', and replaces spaces with underscores.
        """
        stem = Path(filename).stem
        suffix = Path(filename).suffix

        # Remove "Copy of " prefix
        stem = re.sub(r'^Copy of\s+', '', stem, flags=re.IGNORECASE)
        # Remove trailing (1), (2) etc often added by OS for duplicates
        stem = re.sub(r'\s*\(\d+\)$', '', stem)
        # Replace spaces and dots in name with underscores
        stem = re.sub(r'[\s\.]+', '_', stem)
        
        return f"{stem}{suffix}"

    def create_plan(self, source: Path, domain: str, theme: str, is_duplicate: bool) -> ActionPlan:
        if is_duplicate:
            return ActionPlan(
                source=source,
                destination=Path("TRASH"), # Placeholder, handled in execute
                action_type='TRASH',
                reason="Duplicate file detected"
            )

        # Apply smart renaming
        new_filename = self._smart_rename(source.name)

        # Construct destination
        dest_path = self.root_destination / domain / theme / new_filename
        
        # Safety check: Don't move if source and dest are same
        if source.resolve() == dest_path.resolve():
             return ActionPlan(
                source=source,
                destination=dest_path,
                action_type='SKIP',
                reason="File already in correct location"
            )

        return ActionPlan(source=source, destination=dest_path, action_type='MOVE', reason=f"Organized into {domain}/{theme}")