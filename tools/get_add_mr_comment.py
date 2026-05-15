import urllib.parse
import requests
from langchain_core.tools import tool
from config import GITLAB_URL, HEADERS
import re





@tool
def add_mr_comment(project: str, mr_no: int, comment: str):
    """
    Add a general comment to a GitLab Merge Request.

    Use this tool when:
    - MR review is completed
    - You want to provide feedback or suggestions
    - Reporting bugs, risks, or improvements
    
    """
    try:
        encoded_project = urllib.parse.quote_plus(project)

        url = (
            f"{GITLAB_URL}/api/v4/projects/"
            f"{encoded_project}/merge_requests/"
            f"{mr_no}/notes"
        )

        payload = {
            "body": comment
        }

        response = requests.post(url, headers=HEADERS,json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "note_id": data.get("id"),
            "web_url": data.get("url"),
            "comment": comment
        }


    except Exception as e:
        return {"success": False,"error": str(e)}
