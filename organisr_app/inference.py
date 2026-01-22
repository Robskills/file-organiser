from typing import Tuple
from models import FileContext, ClassificationResult
from taxonomy import TAXONOMY, SCORE_EXACT_KEYWORD, SCORE_PARTIAL_KEYWORD, SCORE_EXTENSION, SCORE_PARENT_FOLDER

class InferenceEngine:
    def classify(self, context: FileContext) -> ClassificationResult:
        best_domain = "Unsorted"
        best_theme = "Misc"
        max_score = 0.0
        reasons = []

        clean_name = context.filename.lower()
        clean_ext = context.extension.lower().replace('.', '')
        clean_parent = context.parent_folder.lower()

        for domain, themes in TAXONOMY.items():
            for theme, rules in themes.items():
                current_score = 0.0
                current_reasons = []

                # 1. Check Extensions
                if clean_ext in rules.get("ext", []):
                    current_score += SCORE_EXTENSION
                    current_reasons.append(f"Extension match (.{clean_ext})")

                # 2. Check Keywords in Filename
                for kw in rules.get("keywords", []):
                    kw = kw.lower()
                    # Exact word match (splitting by common delimiters)
                    parts = clean_name.replace('_', ' ').replace('-', ' ').replace('.', ' ').split()
                    if kw in parts:
                        current_score += SCORE_EXACT_KEYWORD
                        current_reasons.append(f"Exact keyword match '{kw}'")
                    elif kw in clean_name:
                        current_score += SCORE_PARTIAL_KEYWORD
                        current_reasons.append(f"Partial keyword match '{kw}'")

                # 3. Check Parent Folder Context
                # If the file is already in a folder named "Invoices", that's a strong signal
                if domain.lower() in clean_parent or theme.lower() in clean_parent:
                    current_score += SCORE_PARENT_FOLDER
                    current_reasons.append(f"Context match '{context.parent_folder}'")

                # Update Best Score
                if current_score > max_score:
                    max_score = current_score
                    best_domain = domain
                    best_theme = theme
                    reasons = current_reasons

        # Cap score at 1.0
        max_score = min(max_score, 1.0)

        return ClassificationResult(
            domain=best_domain,
            theme=best_theme,
            confidence=max_score,
            reason=reasons
        )

    def infer_destination(self, context: FileContext) -> ClassificationResult:
        """
        Main entry point for classification.
        """
        result = self.classify(context)
        
        if not result.is_confident:
            return ClassificationResult(
                domain="Unsorted",
                theme=context.extension.replace('.', '').upper() or "No_Extension",
                confidence=result.confidence,
                reason=["Low confidence"]
            )
        return result