from typing import Tuple, List
from models import FileContext
from taxonomy import TAXONOMY, SCORE_EXACT_KEYWORD, SCORE_PARTIAL_KEYWORD, SCORE_EXTENSION, SCORE_PARENT_FOLDER

class ThemeInference:
    def infer_theme(self, context: FileContext, domain: str = None) -> Tuple[str, float, List[str]]:
        """
        Infers the best theme. If domain is provided, only checks themes in that domain.
        Returns (theme_path, score, reasons).
        """
        clean_name = context.filename.lower()
        clean_ext = context.extension.lower().replace('.', '')
        clean_parent = context.parent_folder.lower()

        # Determine which part of taxonomy to search
        search_space = {domain: TAXONOMY[domain]} if domain and domain in TAXONOMY else TAXONOMY
        
        # If we are searching a specific domain, we want to search INSIDE it, not the domain key itself
        if domain:
            search_space = TAXONOMY[domain]

        return self._recursive_search(search_space, context, clean_name, clean_ext, clean_parent)

    def _recursive_search(self, node: dict, context: FileContext, clean_name: str, clean_ext: str, clean_parent: str) -> Tuple[str, float, List[str]]:
        # Base case: If this node has rules (ext/keywords), evaluate it
        if "ext" in node or "keywords" in node:
            return self._evaluate_rules(node, context, clean_name, clean_ext, clean_parent)

        best_path = "Misc"
        max_score = 0.0
        best_reasons = []

        for key, subnode in node.items():
            # Recursive step
            sub_path, score, reasons = self._recursive_search(subnode, context, clean_name, clean_ext, clean_parent)
            
            if score > max_score:
                max_score = score
                # If sub_path is empty (leaf node matched), just use key. Else join key/sub_path
                best_path = f"{key}/{sub_path}" if sub_path else key
                best_reasons = reasons

        # If no child matched well, return default
        if max_score == 0.0:
            return "", 0.0, []

        return best_path, max_score, best_reasons

    def _evaluate_rules(self, rules: dict, context: FileContext, clean_name: str, clean_ext: str, clean_parent: str) -> Tuple[str, float, List[str]]:
        current_score = 0.0
        current_reasons = []

        # 1. Check Extensions
        if clean_ext in rules.get("ext", []):
            current_score += SCORE_EXTENSION
            current_reasons.append(f"Extension match (.{clean_ext})")

        # 2. Check Keywords
        for kw in rules.get("keywords", []):
            kw = kw.lower()
            parts = clean_name.replace('_', ' ').replace('-', ' ').replace('.', ' ').split()
            if kw in parts:
                current_score += SCORE_EXACT_KEYWORD
                current_reasons.append(f"Exact keyword match '{kw}'")
            elif kw in clean_name:
                current_score += SCORE_PARTIAL_KEYWORD
                current_reasons.append(f"Partial keyword match '{kw}'")

        # 3. Check Parent Folder (Context)
        # Note: In recursive logic, we might want to pass the current 'key' as the theme name to check
        # For simplicity, we check if the parent folder matches any known keywords in the rules
        if any(k in clean_parent for k in rules.get("keywords", [])):
             current_score += SCORE_PARENT_FOLDER
             current_reasons.append(f"Context match '{context.parent_folder}'")

        return "", current_score, current_reasons