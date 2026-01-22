import json
import logging
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

# Ensure project root is in sys.path so we can import organisr_app modules
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Import core logic
from organisr_app import taxonomy
from organisr_app.config import APP_VERSION, DEST_DIR, SOURCE_DIRS, THEME_MODE
from organisr_app.main import run_organizer_logic
from organisr_app.scheduler import schedule_weekly_task
from organisr_app.updater import UpdateChecker

class TextHandler(logging.Handler):
    """Logging handler that writes to a Tkinter Text widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)

class OrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer Pro")
        self.root.geometry("900x700")
        
        self.theme_mode = tk.StringVar(value=THEME_MODE)

        # Variables
        self.source_path = tk.StringVar(value=str(SOURCE_DIRS[0]) if SOURCE_DIRS else "")
        self.dest_path = tk.StringVar(value=str(DEST_DIR))
        self.dry_run_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")
        self.user_context_var = tk.StringVar(value=", ".join(taxonomy.USER_CONTEXT_KEYWORDS))
        
        self._setup_styles()
        self._setup_tabs()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        is_dark = self.theme_mode.get() == "dark"
        
        # Dark Theme Palette
        if is_dark:
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            accent_color = "#007acc"
            entry_bg = "#3c3f41"
            self.root.configure(bg=bg_color)
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            accent_color = "#0078d7"
            entry_bg = "#ffffff"
            self.root.configure(bg=bg_color)
        
        # General Configuration
        style.configure(".", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        
        # Buttons
        style.configure("TButton", background=accent_color, foreground=fg_color, borderwidth=0, padding=8, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[('active', '#005f9e'), ('disabled', '#555555')])
        
        # Entries
        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color, borderwidth=0, padding=5)
        
        # LabelFrames
        style.configure("TLabelframe", background=bg_color, foreground=fg_color, bordercolor="#444444")
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color, font=("Segoe UI", 11, "bold"))
        
        # Checkbutton
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[('active', bg_color)])
        
        # Progressbar
        style.configure("Horizontal.TProgressbar", background=accent_color, troughcolor=entry_bg, bordercolor=bg_color)

        # Notebook
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color, padding=[10, 5], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", accent_color)], foreground=[("selected", "#ffffff")])

    def _setup_tabs(self):
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.run_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.run_tab, text="Organizer")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")

        self._setup_run_ui(self.run_tab)
        self._setup_settings_ui(self.settings_tab)
        self._setup_about_ui(self.about_tab)

    def _setup_run_ui(self, parent):
        # Main Container
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_lbl = ttk.Label(main_frame, text="Organisr AI", font=("Segoe UI", 24, "bold"), foreground="#007acc")
        header_lbl.pack(pady=(0, 20))

        # Source Selection
        src_frame = ttk.LabelFrame(main_frame, text="Source Directory", padding="5")
        src_frame.pack(fill=tk.X, pady=10)
        
        src_inner = ttk.Frame(src_frame)
        src_inner.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(src_inner, textvariable=self.source_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(src_inner, text="Browse", command=self._browse_source).pack(side=tk.RIGHT)

        # Destination Selection
        dst_frame = ttk.LabelFrame(main_frame, text="Destination Directory", padding="5")
        dst_frame.pack(fill=tk.X, pady=10)
        
        dst_inner = ttk.Frame(dst_frame)
        dst_inner.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(dst_inner, textvariable=self.dest_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(dst_inner, text="Browse", command=self._browse_dest).pack(side=tk.RIGHT)

        # Options
        opt_frame = ttk.Frame(main_frame)
        opt_frame.pack(fill=tk.X, pady=10)
        ttk.Checkbutton(opt_frame, text="Dry Run (Simulate only)", variable=self.dry_run_var).pack(side=tk.LEFT)
        
        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        self.run_btn = ttk.Button(btn_frame, text="Start Organization", command=self._start_process)
        self.run_btn.pack(side=tk.LEFT, padx=10, ipadx=10)
        
        self.audit_btn = ttk.Button(btn_frame, text="AI Space Audit", command=self._start_audit)
        self.audit_btn.pack(side=tk.LEFT, padx=10, ipadx=10)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            state='disabled', 
            height=15, 
            bg="#1e1e1e", 
            fg="#d4d4d4", 
            font=("Consolas", 9),
            insertbackground="white",
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.FLAT, anchor=tk.W, background="#007acc", foreground="white", padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Setup Logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _setup_settings_ui(self, parent):
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Local Intelligence Settings ---
        ai_frame = ttk.LabelFrame(main_frame, text="Local Intelligence Configuration", padding="10")
        ai_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(ai_frame, text="Organization Focus Area (Functional Utility):").pack(anchor=tk.W)
        
        key_frame = ttk.Frame(ai_frame)
        key_frame.pack(fill=tk.X, pady=5)
        
        self.context_entry = ttk.Entry(key_frame, textvariable=self.user_context_var)
        self.context_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(key_frame, text="Update Focus", command=self._save_user_context).pack(side=tk.RIGHT)
        
        ttk.Label(ai_frame, text="Enter keywords separated by commas (e.g. 'Thesis, Finance, ProjectX') to bias the local AI.", font=("Segoe UI", 9, "italic")).pack(anchor=tk.W)

        # --- Taxonomy Editor ---
        lbl = ttk.Label(main_frame, text="Edit Taxonomy Rules (JSON)", font=("Segoe UI", 12, "bold"))
        lbl.pack(pady=(0, 10), anchor=tk.W)

        self.settings_text = scrolledtext.ScrolledText(
            main_frame, 
            font=("Consolas", 10),
            bg="#1e1e1e", 
            fg="#d4d4d4",
            insertbackground="white",
            borderwidth=0
        )
        self.settings_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Load current config
        self._reload_settings()

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="Save Changes", command=self._save_settings)
        save_btn.pack(side=tk.RIGHT)
        
        sched_btn = ttk.Button(btn_frame, text="Schedule Weekly Run", command=self._schedule_task)
        sched_btn.pack(side=tk.LEFT)
        
        reset_btn = ttk.Button(btn_frame, text="Reload Current", command=self._reload_settings)
        reset_btn.pack(side=tk.RIGHT, padx=10)

    def _setup_about_ui(self, parent):
        frame = ttk.Frame(parent, padding=40)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="File Organizer Pro", font=("Segoe UI", 24, "bold")).pack()
        ttk.Label(frame, text=f"Version {APP_VERSION}", font=("Segoe UI", 12)).pack(pady=(0, 20))
        
        ttk.Label(frame, text="A modular, AI-enhanced file organization tool.").pack()
        
        ttk.Button(frame, text="Check for Updates", command=self._check_updates).pack(pady=30)
        
        # Theme Toggle
        ttk.Label(frame, text="Theme Settings:").pack(pady=(20, 5))
        theme_frame = ttk.Frame(frame)
        theme_frame.pack()
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_mode, value="dark", command=self._setup_styles).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_mode, value="light", command=self._setup_styles).pack(side=tk.LEFT, padx=10)

    def _save_user_context(self):
        raw_text = self.user_context_var.get()
        keywords = [k.strip() for k in raw_text.split(',') if k.strip()]
        
        # Update taxonomy config
        current_config = taxonomy.get_editable_config()
        current_config["USER_CONTEXT_KEYWORDS"] = keywords
        taxonomy.apply_config(current_config)
        
        messagebox.showinfo("Updated", "Local Intelligence focus updated successfully.")

    def _schedule_task(self):
        success, msg = schedule_weekly_task()
        if success:
            messagebox.showinfo("Scheduler", msg)
        else:
            messagebox.showerror("Scheduler Error", msg)

    def _check_updates(self):
        has_update, latest, url = UpdateChecker.check_for_updates()
        if has_update:
            if messagebox.askyesno("Update Available", f"Version {latest} is available.\n\nDo you want to download it now?"):
                webbrowser.open(url if url else "https://github.com/organisr/releases")
        else:
            messagebox.showinfo("Up to Date", f"You are running the latest version ({APP_VERSION}).")

    def _save_settings(self):
        try:
            text = self.settings_text.get("1.0", tk.END)
            config = json.loads(text)
            taxonomy.apply_config(config)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _reload_settings(self):
        self.settings_text.delete("1.0", tk.END)
        config = taxonomy.get_editable_config()
        self.settings_text.insert("1.0", json.dumps(config, indent=4))

    def _browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)

    def _browse_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path.set(path)

    def _start_audit(self):
        # Force dry run for audit
        self._start_process(force_dry_run=True, audit_mode=True)

    def _start_process(self, force_dry_run=False, audit_mode=False):
        source = Path(self.source_path.get())
        dest = Path(self.dest_path.get())
        dry_run = True if force_dry_run else self.dry_run_var.get()

        if not source.exists():
            self.logger.error("Source directory does not exist!")
            return

        self.run_btn.config(state='disabled')
        self.audit_btn.config(state='disabled')
        self.progress.start(10)
        mode_text = "Auditing..." if audit_mode else "Running..."
        self.status_var.set(mode_text)

        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._run_logic, args=(source, dest, dry_run))
        thread.daemon = True
        thread.start()

    def _run_logic(self, source, dest, dry_run):
        try:
            user_context = self.user_context_var.get()
            results = run_organizer_logic(source_dirs=[source], dest_dir=dest, dry_run=dry_run, user_context=user_context)
            
            count = results["count"]
            duration = results["duration"]
            msg = f"Completed! Organized {count} files in {duration:.2f} seconds."
            self.logger.info(msg)
            self.logger.info(results["ai_report"]) # Print AI report to log window
            self.root.after(0, lambda: self.status_var.set(msg))
            self.root.after(0, lambda: self._on_finish(results, dry_run))
        except Exception as e:
            self.logger.error(f"Error: {e}")
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.run_btn.config(state='normal'))
            self.root.after(0, lambda: self.audit_btn.config(state='normal'))

    def _on_finish(self, results, dry_run):
        """Handles post-processing popups."""
        # 1. Summary Popup
        summary = (
            f"Organization Complete!\n\n"
            f"Files Processed: {results['count']}\n"
            f"Time Taken: {results['duration']:.2f}s\n"
            f"Files Moved: {len(results['moved_files'])}\n"
            f"New Folders Created: {len(results['created_folders'])}\n"
        )
        
        if results['created_folders']:
            summary += "\nNew Folders:\n" + "\n".join([Path(p).name for p in results['created_folders'][:5]])
            if len(results['created_folders']) > 5:
                summary += "\n...and more."

        messagebox.showinfo("Summary", summary)

        # 2. Empty Folder Deletion (Only if not dry run)
        if not dry_run and results['empty_folders']:
            count = len(results['empty_folders'])
            msg = (
                f"Found {count} empty folders in the source directory after organization.\n\n"
                "Do you want to delete them to clean up?"
            )
            if messagebox.askyesno("Cleanup Empty Folders", msg):
                self._delete_empty_folders(results['empty_folders'])

    def _delete_empty_folders(self, folders):
        deleted_count = 0
        for folder in folders:
            try:
                # Double check it's still empty and exists
                p = Path(folder)
                if p.exists() and not any(p.iterdir()):
                    p.rmdir()
                    deleted_count += 1
                    self.logger.info(f"Deleted empty folder: {folder}")
            except Exception as e:
                self.logger.error(f"Failed to delete {folder}: {e}")
        
        messagebox.showinfo("Cleanup Complete", f"Deleted {deleted_count} empty folders.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizerGUI(root)
    root.mainloop()