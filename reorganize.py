import os
import shutil
from pathlib import Path

def reorganize():
    # Define the base directory (root of the project)
    base_dir = Path(__file__).resolve().parent
    
    # Define the new app directory
    app_dir = base_dir / "organisr_app"
    app_dir.mkdir(exist_ok=True)
    
    # Create __init__.py to make it a package
    (app_dir / "__init__.py").touch()
    
    # List of files to move
    files_to_move = [
        "actions.py",
        "ai_optimizer.py",
        "ai_service.py",
        "config.py",
        "deduplicator.py",
        "domain_inference.py",
        "gui.py",
        "inference.py",
        "logger.py",
        "main.py",
        "models.py",
        "scanner.py",
        "scheduler.py",
        "security.py",
        "taxonomy.py",
        "theme_inference.py",
        "updater.py"
    ]
    
    print(f"Moving files to {app_dir}...")
    
    for filename in files_to_move:
        src = base_dir / filename
        dst = app_dir / filename
        
        if src.exists():
            try:
                shutil.move(str(src), str(dst))
                print(f"Moved: {filename}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"Skipped (not found): {filename}")
            
    print("\nReorganization complete.")
    print("You can now run the app using: python organisr_app/gui.py")

if __name__ == "__main__":
    reorganize()