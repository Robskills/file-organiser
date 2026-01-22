import logging
import re
import difflib

logger = logging.getLogger(__name__)

class LocalIntelligenceEngine:
    """
    A robust, local, rule-based intelligence engine that simulates semantic understanding
    using advanced heuristics, fuzzy matching, and concept association graphs.
    Replaces external LLM dependencies with local 'tricks'.
    """
    def __init__(self, user_context: str = ""):
        self.enabled = True
        # Parse user context keywords (e.g., "University, Thesis") to boost specific scores
        self.user_context = [w.lower().strip() for w in user_context.split(',') if w.strip()]
        self._build_knowledge_base()

    def is_active(self):
        return self.enabled

    def _build_knowledge_base(self):
        """
        Constructs a local semantic graph mapping concepts to potential categories.
        This acts as the 'brain' of the local AI.
        Structure: Keyword -> (Group, Path, BaseWeight)
        """
        self.concepts = {
            # Finance & Admin
            "invoice": ("Documents", "Finance/Invoices", 0.9),
            "receipt": ("Documents", "Finance/Invoices", 0.9),
            "bill": ("Documents", "Finance/Invoices", 0.8),
            "tax": ("Documents", "Finance/Taxes", 0.9),
            "statement": ("Documents", "Finance/Statements", 0.8),
            "ledger": ("Documents", "Finance/Accounting", 0.7),
            "payroll": ("Documents", "Work/HR", 0.8),
            "contract": ("Documents", "Work/Legal", 0.9),
            "agreement": ("Documents", "Work/Legal", 0.8),
            
            # Academic / Education
            "thesis": ("Documents", "Education/Research", 0.95),
            "dissertation": ("Documents", "Education/Research", 0.95),
            "assignment": ("Documents", "Education/Assignments", 0.8),
            "lecture": ("Documents", "Education/Materials", 0.7),
            "syllabus": ("Documents", "Education/Admin", 0.8),
            "exam": ("Documents", "Education/Exams", 0.8),
            "quiz": ("Documents", "Education/Exams", 0.8),
            "lab": ("Documents", "Education/Labs", 0.7),
            
            # Tech / Dev
            "main": ("Documents", "Computer Science/Code", 0.6),
            "script": ("Documents", "Computer Science/Code", 0.6),
            "config": ("Documents", "Computer Science/Config", 0.7),
            "log": ("Documents", "Computer Science/Logs", 0.8),
            "backup": ("Archives", "Backups", 0.9),
            "dump": ("Archives", "Backups", 0.7),
            "database": ("Documents", "Computer Science/Data", 0.8),
            
            # Media & Entertainment
            "track": ("Media", "Music", 0.6),
            "mix": ("Media", "Music", 0.6),
            "episode": ("Media", "TV Shows", 0.8),
            "season": ("Media", "TV Shows", 0.8),
            "trailer": ("Media", "Movies", 0.8),
            "footage": ("Media", "Video/Raw", 0.7),
            "render": ("Media", "Video/Renders", 0.8),
            
            # Personal
            "resume": ("Documents", "Work/Career", 0.95),
            "cv": ("Documents", "Work/Career", 0.95),
            "letter": ("Documents", "Personal/Letters", 0.6),
            "ticket": ("Documents", "Personal/Travel", 0.8),
            "booking": ("Documents", "Personal/Travel", 0.8),
            "itinerary": ("Documents", "Personal/Travel", 0.8),
            "scan": ("Documents", "Scans", 0.6),
        }
        
        # Extension associations to validate semantic guesses
        self.ext_associations = {
            ".pdf": ["Documents"],
            ".docx": ["Documents"],
            ".xlsx": ["Documents", "Finance"],
            ".csv": ["Documents", "Data"],
            ".py": ["Computer Science", "Work"],
            ".js": ["Computer Science", "Work"],
            ".jpg": ["Images", "Personal"],
            ".png": ["Images", "Screenshots"],
            ".mp4": ["Media", "Video"],
            ".mp3": ["Media", "Music"]
        }

    def classify_file(self, filename: str, extension: str):
        """
        Analyzes the filename using local heuristics.
        Returns: (Group, Path, Score, Reasons) or None.
        """
        try:
            # 1. Tokenize and Clean
            tokens = self._tokenize(filename)
            
            # 2. Contextual Boosting
            # If user context matches tokens, increase base probability
            context_boost = 0.0
            for ctx in self.user_context:
                if any(ctx in t for t in tokens):
                    context_boost += 0.25
                    
            # 3. Concept Matching
            best_match = None
            highest_score = 0.0
            reasons = []

            for token in tokens:
                # A. Direct match
                if token in self.concepts:
                    cat, subcat, weight = self.concepts[token]
                    score = weight + context_boost
                    if score > highest_score:
                        highest_score = score
                        best_match = (cat, subcat)
                        reasons = [f"Detected concept: '{token}'"]
                
                # B. Fuzzy match (Tricks for typos or variations)
                # Check if token is 'close enough' to known concepts
                matches = difflib.get_close_matches(token, self.concepts.keys(), n=1, cutoff=0.85)
                if matches:
                    match_key = matches[0]
                    cat, subcat, weight = self.concepts[match_key]
                    # Penalty for fuzzy match
                    score = (weight * 0.85) + context_boost
                    if score > highest_score:
                        highest_score = score
                        best_match = (cat, subcat)
                        reasons = [f"Fuzzy match: '{token}' ~ '{match_key}'"]

            # 4. Extension Validation
            # If we found a match, verify if extension makes sense
            if best_match:
                group, path = best_match
                valid_groups = self.ext_associations.get(extension.lower(), [])
                
                # If extension strongly contradicts the semantic guess (e.g. 'invoice.mp3')
                if valid_groups and group not in valid_groups and "Documents" not in valid_groups:
                    highest_score *= 0.5
                    reasons.append("Extension mismatch penalty")
                elif valid_groups:
                    highest_score += 0.1
                    reasons.append("Extension validation bonus")

            # 5. Final Decision
            if best_match and highest_score > 0.45:
                # Normalize score
                final_score = min(highest_score, 1.0)
                return (
                    best_match[0], # Group
                    best_match[1], # Path
                    final_score,
                    reasons + ["Local Heuristic Analysis"]
                )
            
            return None

        except Exception as e:
            logger.error(f"Local AI analysis failed: {e}")
            return None

    def _tokenize(self, text: str):
        """Splits text into meaningful semantic units."""
        # Replace separators with spaces
        clean = re.sub(r'[_\-\.]', ' ', text)
        # Split camelCase (e.g., 'MyFile' -> 'My File')
        clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean)
        # Remove digits and non-alphanumeric
        clean = re.sub(r'[^a-zA-Z\s]', '', clean)
        
        tokens = clean.lower().split()
        # Filter stop words
        stop_words = {'the', 'a', 'an', 'of', 'for', 'in', 'to', 'at', 'by', 'my', 'new', 'copy', 'final', 'draft', 'v1', 'v2'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]