from ai_service import LocalIntelligenceEngine
from models import FileContext
from taxonomy import (CATEGORY_HIERARCHY, CONFIDENCE_THRESHOLD,
                      EXTENSION_GROUPS, SCORE_EXACT, SCORE_PARTIAL)

class DomainInference:
    def __init__(self, ai_service: LocalIntelligenceEngine = None):
        self.ai_service = ai_service

    def infer_domain_and_theme(self, context: FileContext):
        """
        Performs multi-level hierarchical classification.
        Returns (ExtensionGroup, PathString, Score, Reasons)
        """
        # 0. Level 0: AI Classification (if enabled)
        if self.ai_service and self.ai_service.is_active():
            ai_result = self.ai_service.classify_file(context.filename, context.extension)
            if ai_result:
                # Unpack AI result: (Group, Path, Score, Reasons)
                # We trust AI with a high base confidence if it returns a result
                return ai_result

        # 1. Level 1: Extension Group
        ext_group = self._get_extension_group(context.extension)
        
        # 2. Level 2: Primary Category
        primary_cat, primary_score, primary_reasons = self._get_best_match(
            context.filename, 
            {k: v["keywords"] for k, v in CATEGORY_HIERARCHY.items()}
        )

        if primary_score < CONFIDENCE_THRESHOLD:
            return ext_group, "Unsorted", primary_score, ["Low confidence in primary category"]

        # 3. Level 3: Secondary Subcategory
        subcats = CATEGORY_HIERARCHY[primary_cat]["subcategories"]
        secondary_cat, secondary_score, secondary_reasons = self._get_best_match(
            context.filename,
            subcats
        )

        if secondary_score < CONFIDENCE_THRESHOLD:
            # Primary found, but no specific subcategory
            return ext_group, f"{primary_cat}/Unsorted", primary_score, primary_reasons + ["No subcategory match"]

        # Full match
        full_path = f"{primary_cat}/{secondary_cat}"
        combined_reasons = primary_reasons + secondary_reasons
        return ext_group, full_path, secondary_score, combined_reasons

    def _get_extension_group(self, extension: str) -> str:
        ext = extension.lower()
        for group, extensions in EXTENSION_GROUPS.items():
            if ext in extensions:
                return group
        return "Unsorted_Extensions"

    def _get_best_match(self, filename: str, candidates: dict) -> tuple:
        best_cat = None
        max_score = 0.0
        reasons = []
        
        clean_name = filename.lower().replace('.', ' ').replace('_', ' ').replace('-', ' ')
        name_parts = set(clean_name.split())

        for cat, keywords in candidates.items():
            current_score = 0.0
            current_reasons = []
            
            for kw in keywords:
                kw = kw.lower()
                if kw in name_parts: # Exact word match
                    current_score += SCORE_EXACT
                    current_reasons.append(f"Matched keyword '{kw}'")
                elif kw in clean_name: # Partial match
                    current_score += SCORE_PARTIAL
                    current_reasons.append(f"Partial match '{kw}'")
            
            if current_score > max_score:
                max_score = current_score
                best_cat = cat
                reasons = current_reasons
        
        return best_cat, max_score, reasons