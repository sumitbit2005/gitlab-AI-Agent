import urllib.parse
import requests
from langchain_core.tools import tool
from config import GITLAB_URL, HEADERS


@tool
def get_mr_changes(project:str, mr_no: int):
    """
    Fetch GitLab Merge Request Changes details.

    Args:
        project: GitLab project path.
                 Example: mygroup/myrepo

        mr_no: Merge Request number (IID)
    """
    try:
        encoded_project = urllib.parse.quote_plus(project)

        url = (
            f"{GITLAB_URL}/api/v4/projects/"
            f"{encoded_project}/merge_requests/"
            f"{mr_no}/changes"
        )

        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()

        return {
        "title": data.get("title"),
        "description": data.get("description"),
        "state": data.get("state"),
        "author": data.get("author", {}).get("name"),
        "source_branch": data.get("source_branch"),
        "target_branch": data.get("target_branch"),
        "web_url": data.get("web_url"),
        "created_at": data.get("created_at"),

        "changes_count": data.get("changes_count"),

        "changes": [
            {
            "old_path": change.get("old_path"),
            "new_path": change.get("new_path"),

            "new_file": change.get("new_file"),
            "deleted_file": change.get("deleted_file"),
            "renamed_file": change.get("renamed_file"),

            "diff": change.get("diff"),
            }
            for change in data.get("changes", [])
                    ]
}

    except Exception as e:
        return {"error": str(e)}