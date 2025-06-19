import json
import requests
from .config import APPROVAL_SERVER_URL


def request_approval(file_info: dict) -> bool:
    """Send approval request to remote machine."""
    try:
        resp = requests.post(APPROVAL_SERVER_URL, json=file_info, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("approved", False)
    except Exception:
        return False
