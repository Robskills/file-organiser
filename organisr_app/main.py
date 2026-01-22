import logging
import time
import os
import argparse
from pathlib import Path
from config import SOURCE_DIRS, DEST_DIR, DRY_RUN
from logger import setup_logging
from scanner import FileScanner
from deduplicator import Deduplicator
from domain_inference import DomainInference
from actions import ActionExecutor
from ai_optimizer import AIOptimizer
from ai_service import LocalIntelligenceEngine

def get_global_defaults():
    """Returns default source and destination paths for the current user."""
    home = Path.home()
    sources = [
        home / "Downloads",
        home / "Desktop",
        home / "Documents"
    ]
    sources = [p for p in sources if p.exists()]
    dest = home / "Documents" / "Organized"
    return sources, dest

def run_organizer_logic(source_dirs, dest_dir, dry_run=True, user_context=""):
    """
    Core logic wrapper to allow calling from GUI or CLI.
    Returns (count_of_files, time_taken_seconds, ai_report)
    """
    logger = logging.getLogger(__name__)
    
    # Global Fallback: If no sources selected, check default home folders
    if not source_dirs:
        logger.info("No source directories selected. Checking global default folders...")
        source_dirs, default_dest = get_global_defaults()
        if not dest_dir:
            dest_dir = default_dest

    start_time = time.time()
    scanner = FileScanner(source_dirs)
    deduplicator = Deduplicator()
    
    # Initialize Local AI Service
    ai_service = LocalIntelligenceEngine(user_context)
    domain_engine = DomainInference(ai_service=ai_service)
    
    executor = ActionExecutor(dest_dir, dry_run=dry_run)
    ai_optimizer = AIOptimizer()

    count = 0
    for context in scanner.scan():
        count += 1
        logger.info(f"Processing: {context.filename}")

        # 1. Check Duplicates
        is_dup = deduplicator.is_duplicate(context)
        
        # 2. AI Analysis (Space & Structure)
        ai_optimizer.analyze(context)
        
        # 3. Inference
        domain, theme, score, reasons = domain_engine.infer_domain_and_theme(context)
        
        # 4. Create Action Plan
        plan = executor.create_plan(
            source=context.path,
            domain=domain,
            theme=theme,
            is_duplicate=is_dup
        )

        # 5. Execute
        executor.execute(plan)

    # Generate AI Report
    ai_optimizer.infer_structure()
    space_report = ai_optimizer.get_space_report()
    structure_report = "\n".join(ai_optimizer.proposals["suggested_folders"])
    full_report = f"\n--- AI OPTIMIZER REPORT ---\n{space_report}\n\n{structure_report}\n---------------------------"

    # Find empty folders in source directories (Post-organization cleanup)
    empty_folders = []
    if not dry_run:
        for src in source_dirs:
            if src.exists():
                for root, dirs, files in os.walk(src, topdown=False):
                    for name in dirs:
                        d = Path(root) / name
                        try:
                            # Check if directory is empty
                            if not any(d.iterdir()):
                                empty_folders.append(str(d))
                        except OSError:
                            pass

    duration = time.time() - start_time
    
    # Return comprehensive results dict
    return {
        "count": count,
        "duration": duration,
        "ai_report": full_report,
        "moved_files": executor.moved_files,
        "created_folders": list(executor.created_folders),
        "empty_folders": empty_folders
    }

def main():
    parser = argparse.ArgumentParser(description="File Organizer Pro CLI")
    parser.add_argument("--force", action="store_true", help="Force execution (disable dry-run)")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Organizer CLI...")

    # Determine dry_run status: --force overrides config
    is_dry_run = False if args.force else DRY_RUN

    # Check if configured sources exist, otherwise pass empty list to trigger global fallback
    sources = SOURCE_DIRS
    if not sources or not any(p.exists() for p in sources):
        sources = []

    results = run_organizer_logic(sources, DEST_DIR, is_dry_run)
    
    logger.info(f"Organization complete. Processed {results['count']} files in {results['duration']:.2f} seconds.")
    logger.info(results['ai_report'])

if __name__ == "__main__":
    main()