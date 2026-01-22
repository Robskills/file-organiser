from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict
from models import FileContext

class AIOptimizer:
    def __init__(self):
        self.stats = {
            "total_size": 0,
            "file_count": 0,
            "extensions": Counter(),
            "keywords": Counter(),
        }
        self.proposals = {
            "delete_old_installers": [],
            "delete_temp_files": [],
            "suggested_folders": []
        }

    def analyze(self, context: FileContext):
        """Analyzes a single file to update stats and check for optimization opportunities."""
        self.stats["file_count"] += 1
        self.stats["total_size"] += context.size_bytes
        self.stats["extensions"][context.extension.lower()] += 1
        
        # Keyword analysis for structure inference (Simple NLP)
        clean_name = context.filename.lower().replace('.', ' ').replace('_', ' ').replace('-', ' ')
        words = [w for w in clean_name.split() if len(w) > 3 and w.isalpha()]
        self.stats["keywords"].update(words)

        # Space Management Logic
        self._check_deletable(context)

    def _check_deletable(self, context: FileContext):
        # 1. Old Installers (> 60 days)
        if context.extension.lower() in ['.exe', '.msi', '.dmg', '.pkg', '.iso']:
            try:
                mtime = datetime.fromtimestamp(context.path.stat().st_mtime)
                if datetime.now() - mtime > timedelta(days=60):
                    self.proposals["delete_old_installers"].append(context)
            except OSError:
                pass

        # 2. Temp Files
        if context.extension.lower() in ['.tmp', '.log', '.bak', '.chk', '.dmp']:
             self.proposals["delete_temp_files"].append(context)

    def infer_structure(self) -> List[str]:
        """
        Proposes a folder structure based on high-frequency keywords (Clustering).
        """
        suggestions = []
        # If a keyword appears in > 5% of files, it's a candidate for a category
        threshold = max(3, self.stats["file_count"] * 0.05)
        
        for word, count in self.stats["keywords"].most_common(10):
            if count >= threshold:
                suggestions.append(f"Detected cluster: '{word.title()}' ({count} files). Suggestion: Create folder '{word.title()}'")
        
        self.proposals["suggested_folders"] = suggestions
        return suggestions

    def get_space_report(self) -> str:
        saved_space = 0
        report = []
        
        installers_size = sum(f.size_bytes for f in self.proposals["delete_old_installers"])
        if installers_size > 0:
            report.append(f"[Space] Found {len(self.proposals['delete_old_installers'])} old installers ({installers_size/1024/1024:.2f} MB) suitable for deletion.")
            saved_space += installers_size

        temp_size = sum(f.size_bytes for f in self.proposals["delete_temp_files"])
        if temp_size > 0:
            report.append(f"[Space] Found {len(self.proposals['delete_temp_files'])} temporary files ({temp_size/1024/1024:.2f} MB) suitable for deletion.")
            saved_space += temp_size

        if saved_space == 0:
            report.append("[Space] No significant space saving opportunities found.")
        else:
            report.append(f"[Summary] Total potential space savings: {saved_space/1024/1024:.2f} MB")
            
        return "\n".join(report)