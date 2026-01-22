import subprocess
import os
import sys
import shutil

GIT_CMD = "git"

def resolve_git_path():
    global GIT_CMD
    if shutil.which("git"):
        return True
    
    # Check common Windows paths
    common_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe")
    ]
    for path in common_paths:
        if os.path.exists(path):
            GIT_CMD = path
            return True
    return False

def run_git_command(args):
    try:
        result = subprocess.run([GIT_CMD] + args, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running '{GIT_CMD} {' '.join(args)}':")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Executable '{GIT_CMD}' not found.")
        return False

def main():
    print("--- GitHub Setup Assistant ---")
    
    if not resolve_git_path():
        print("Git not found in PATH or common locations.")
        user_path = input("Please enter the full path to git.exe (e.g. C:\\Program Files\\Git\\cmd\\git.exe): ").strip().strip('"')
        if os.path.exists(user_path):
            global GIT_CMD
            GIT_CMD = user_path
        else:
            print("Invalid path. Please reinstall Git and ensure it is in your PATH.")
            return

    # 1. Initialize
    if not os.path.exists('.git'):
        print("Initializing Git repository...")
        if not run_git_command(['init']): return
    
    # 2. Add files
    print("Adding files to staging...")
    if not run_git_command(['add', '.']): return
    
    # Check Git Identity
    email_check = subprocess.run([GIT_CMD, 'config', 'user.email'], capture_output=True, text=True)
    name_check = subprocess.run([GIT_CMD, 'config', 'user.name'], capture_output=True, text=True)

    if not email_check.stdout.strip() or not name_check.stdout.strip():
        print("\nGit identity not configured.")
        print("Please enter your details for the commit log (stored locally in .git/config):")
        email = input("Email: ").strip()
        name = input("Name: ").strip()
        
        if email:
            run_git_command(['config', 'user.email', email])
        if name:
            run_git_command(['config', 'user.name', name])

    # 3. Commit
    print("Committing changes...")
    # Check if there are changes to commit
    status = subprocess.run([GIT_CMD, 'status', '--porcelain'], capture_output=True, text=True)
    if status.stdout.strip():
        if not run_git_command(['commit', '-m', 'Update File Organizer Pro']): return
    else:
        print("No changes to commit.")

    # 4. Remote configuration
    try:
        remote_check = subprocess.run([GIT_CMD, 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if remote_check.returncode != 0:
            print("\nNo remote repository configured.")
            print("1. Go to https://github.com/new")
            print("2. Create a new empty repository")
            repo_url = input("3. Paste the repository URL here: ").strip()
            
            if repo_url:
                if not run_git_command(['remote', 'add', 'origin', repo_url]): return
                run_git_command(['branch', '-M', 'main'])
            else:
                print("Skipping push (no URL provided).")
                return
        else:
            print(f"\nRemote 'origin' already configured: {remote_check.stdout.strip()}")
    except FileNotFoundError:
        return

    # 5. Push
    print("\nPushing to GitHub...")
    if not run_git_command(['push', '-u', 'origin', 'main']):
        print("\nPush failed. The remote repository is not empty (e.g., contains a README).")
        print("Attempting to pull and merge remote changes...")
        
        # Try to pull with unrelated histories (since local and remote were init'd separately)
        if run_git_command(['pull', 'origin', 'main', '--allow-unrelated-histories']):
            print("Merge successful. Pushing again...")
            run_git_command(['push', '-u', 'origin', 'main'])
        else:
            print("\nAutomatic merge failed. You may need to resolve conflicts manually.")
            print("To force overwrite the remote (WARNING: deletes remote content), run:")
            print(f'  "{GIT_CMD}" push -f origin main')

if __name__ == "__main__":
    main()