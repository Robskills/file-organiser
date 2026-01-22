import logging
import json
from urllib import request
from config import APP_VERSION, UPDATE_URL

logger = logging.getLogger(__name__)

class UpdateChecker:
    """Checks for application updates asynchronously."""
    
    @staticmethod
    def check_for_updates():
        """
        Checks the update URL for a newer version.
        Returns (has_update, latest_version_str).
        """
        try:
            # Simple timeout to prevent hanging the GUI
            with request.urlopen(UPDATE_URL, timeout=3) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", APP_VERSION).lstrip('v')
                assets = data.get("assets", [])
                download_url = assets[0].get("browser_download_url") if assets else data.get("html_url")
                return latest_version != APP_VERSION, latest_version, download_url
        except Exception as e:
            logger.debug(f"Update check failed: {e}")
            return False, APP_VERSION, None