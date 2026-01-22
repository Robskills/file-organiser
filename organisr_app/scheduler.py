import sys
import subprocess
from pathlib import Path

def schedule_weekly_task():
    """Creates a Windows Task Scheduler task to run the organizer weekly."""
    task_name = "FileOrganizerPro_Weekly"
    
    # Determine executable path
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe
        target = f'"{sys.executable}" --force'
    else:
        # Running as script
        python_exe = sys.executable
        script_path = Path(__file__).parent / "main.py"
        target = f'"{python_exe}" "{script_path}" --force'

    # Command to create task: Weekly on Sundays at 12:00 PM
    cmd = [
        "schtasks", "/Create",
        "/SC", "WEEKLY",
        "/D", "SUN",
        "/ST", "12:00",
        "/TN", task_name,
        "/TR", target,
        "/F",           # Force overwrite if exists
        "/RL", "HIGHEST" # Run with highest privileges
    ]
    
    try:
        # Hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)
        
        if result.returncode == 0:
            return True, "Task scheduled successfully for every Sunday at 12:00 PM."
        else:
            return False, f"Failed to schedule task: {result.stderr}"
    except Exception as e:
        return False, f"Error: {e}"