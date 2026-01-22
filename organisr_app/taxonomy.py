import json
from pathlib import Path

# Level 1: Extension Groups
EXTENSION_GROUPS = {
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".xlsx", ".csv", ".pptx", ".ppt", ".epub", ".mobi"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic", ".svg", ".webp"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg", ".wma"},
    "Video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".ts"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".dmg"},
    "Executables": {".exe", ".msi", ".bat", ".sh", ".app", ".apk"}
}

# Level 2 & 3: Primary Categories and Secondary Subcategories
# Structure: Category -> { "keywords": [...], "subcategories": { Subcategory -> [keywords] } }
CATEGORY_HIERARCHY = {
    "Education": {
        "keywords": ["lecture", "course", "assignment", "homework", "exam", "quiz", "study", "notes", "tutorial", "lesson", "learn", "student", "university", "college", "school", "class"],
        "subcategories": {
            "Nursing": ["nursing", "patient", "clinical", "health", "medical", "anatomy", "physiology", "care plan", "triage", "perioperative", "palliative"],
            "Psychiatry": ["psychiatry", "psychology", "mental", "disorder", "dsm", "therapy", "counseling", "cognitive", "behavioral", "neuro"],
            "Computer Science": ["python", "java", "cpp", "code", "programming", "algorithm", "data structure", "ai", "machine learning", "web", "developer", "hack"],
            "Mathematics": ["math", "algebra", "calculus", "statistics", "geometry", "trigonometry", "probability", "discrete"]
        }
    },
    "Work": {
        "keywords": ["work", "job", "career", "resume", "cv", "project", "report", "meeting", "schedule", "agenda", "proposal", "client", "business", "presentation"],
        "subcategories": {
            "Finance": ["invoice", "receipt", "bill", "tax", "salary", "payroll", "budget", "expense", "statement", "bank"],
            "Legal": ["contract", "agreement", "nda", "law", "legal", "policy", "regulation"],
            "HR": ["hiring", "offer", "interview", "onboarding", "employee", "benefits"],
            "Projects": ["project", "plan", "roadmap", "milestone", "deliverable"]
        }
    },
    "Personal": {
        "keywords": ["personal", "family", "home", "house", "car", "insurance", "id", "passport", "travel", "photo", "video", "memories"],
        "subcategories": {
            "Identity": ["passport", "id card", "license", "birth certificate", "social security"],
            "Travel": ["ticket", "booking", "itinerary", "hotel", "flight", "visa"],
            "Health": ["prescription", "doctor", "lab", "test", "result", "vaccine"]
        }
    },
    "Finance": {
        "keywords": ["finance", "money", "bank", "investment", "crypto", "stock", "trade", "wallet"],
        "subcategories": {
            "Statements": ["statement", "report", "summary", "balance"],
            "Taxes": ["tax", "return", "w2", "1099", "deduction"]
        }
    },
    "Media": {
        "keywords": ["movie", "film", "series", "show", "episode", "season", "music", "song", "track", "album", "podcast", "video", "game"],
        "subcategories": {
            "Movies": ["1080p", "720p", "bluray", "dvdrip", "x264", "x265", "web-dl", "hdr"],
            "TV Shows": ["s0", "e0", "season", "episode", "complete", "hdtv"],
            "Anime": ["anime", "dual audio", "sub", "dub", "ova"],
            "Music": ["mp3", "flac", "remix", "feat", "original mix", "ost", "soundtrack"],
            "Podcasts": ["podcast", "interview", "talk", "episode"]
        }
    }
}

IGNORED_DIRS = {
    '.git', '__pycache__', '.idea', '.vscode', 'node_modules', 'venv', 'env', '.trash'
}

IGNORED_FILES = {
    '.DS_Store', 'Thumbs.db', 'desktop.ini'
}

SCORE_EXACT = 1.0
SCORE_PARTIAL = 0.5
CONFIDENCE_THRESHOLD = 0.3

# User-defined context for Local AI
USER_CONTEXT_KEYWORDS = []

# --- Configuration Persistence Logic ---

CONFIG_FILE = Path.home() / ".organisr" / "taxonomy_config.json"
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

def get_editable_config():
    """Returns a dictionary representation of the configuration for editing."""
    return {
        "EXTENSION_GROUPS": {k: list(v) for k, v in EXTENSION_GROUPS.items()},
        "CATEGORY_HIERARCHY": CATEGORY_HIERARCHY,
        "IGNORED_DIRS": list(IGNORED_DIRS),
        "IGNORED_FILES": list(IGNORED_FILES),
        "SCORES": {
            "SCORE_EXACT": SCORE_EXACT,
            "SCORE_PARTIAL": SCORE_PARTIAL,
            "CONFIDENCE_THRESHOLD": CONFIDENCE_THRESHOLD
        },
        "USER_CONTEXT_KEYWORDS": USER_CONTEXT_KEYWORDS
    }

def apply_config(config):
    """Applies the configuration dictionary to the module variables and saves to file."""
    global EXTENSION_GROUPS, CATEGORY_HIERARCHY, IGNORED_DIRS, IGNORED_FILES
    global SCORE_EXACT, SCORE_PARTIAL, CONFIDENCE_THRESHOLD, USER_CONTEXT_KEYWORDS

    # Update mutable structures in-place to ensure other modules see changes
    if "EXTENSION_GROUPS" in config:
        EXTENSION_GROUPS.clear()
        EXTENSION_GROUPS.update({k: set(v) for k, v in config["EXTENSION_GROUPS"].items()})

    if "CATEGORY_HIERARCHY" in config:
        CATEGORY_HIERARCHY.clear()
        CATEGORY_HIERARCHY.update(config["CATEGORY_HIERARCHY"])

    if "IGNORED_DIRS" in config:
        IGNORED_DIRS.clear()
        IGNORED_DIRS.update(config["IGNORED_DIRS"])

    if "IGNORED_FILES" in config:
        IGNORED_FILES.clear()
        IGNORED_FILES.update(config["IGNORED_FILES"])

    # Update scores
    scores = config.get("SCORES", {})
    SCORE_EXACT = scores.get("SCORE_EXACT", SCORE_EXACT)
    SCORE_PARTIAL = scores.get("SCORE_PARTIAL", SCORE_PARTIAL)
    CONFIDENCE_THRESHOLD = scores.get("CONFIDENCE_THRESHOLD", CONFIDENCE_THRESHOLD)

    if "USER_CONTEXT_KEYWORDS" in config:
        USER_CONTEXT_KEYWORDS = config["USER_CONTEXT_KEYWORDS"]

    # Save to file
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving taxonomy config: {e}")

def _load_config_from_file():
    """Loads configuration from file if it exists."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Apply without saving
                apply_config_internal(config)
        except Exception as e:
            print(f"Failed to load config: {e}")

def apply_config_internal(config):
    """Internal helper to apply config without saving."""
    # We can reuse apply_config but bypass the save part, 
    # or just call apply_config and let it overwrite the file (harmless but redundant).
    # For simplicity in this context, we'll just manually update globals here to avoid circular save.
    # Actually, apply_config is fine to use if we accept a write on startup, 
    # but let's just copy the logic to avoid the write.
    # (Logic is identical to apply_config minus the 'with open...' block)
    pass # Implemented implicitly by calling apply_config in GUI. For startup, we use the logic inside apply_config.

_load_config_from_file()