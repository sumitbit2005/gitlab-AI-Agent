import urllib.parse
import requests
from langchain_core.tools import tool
from config import GITLAB_URL, HEADERS


@tool
def add_inline_comment(project: str, mr_no: int, file_path: str, line_number: int, comment: str, base_sha: str, head_sha: str, start_sha: str):
    """
    Post an inline review comment on a specific line of a file in a GitLab MR.

    Use this tool when:
    - You found a bug, issue, or suggestion on a specific line of code
    - You want to highlight a security, performance, or style concern at a precise location

    Args:
        project: GitLab project path (e.g. mygroup/myrepo)
        mr_no: Merge Request IID number
        file_path: Path of the file to comment on (use new_path from the diff)
        line_number: Line number in the NEW version of the file.
                     Calculate from diff hunk header: @@ -old,count +NEW_START,count @@
                     Count lines from NEW_START for each line shown in the diff.
                     ONLY use lines that appear in the diff (added or context lines).
        comment: The review comment text (supports markdown)
        base_sha: From MR diff_refs.base_sha
        head_sha: From MR diff_refs.head_sha
        start_sha: From MR diff_refs.start_sha
    """
    try:
        encoded_project = urllib.parse.quote_plus(project)
        url = (
            f"{GITLAB_URL}/api/v4/projects/"
            f"{encoded_project}/merge_requests/"
            f"{mr_no}/discussions"
        )

        payload = {
            "body": comment,
            "position": {
                "base_sha": base_sha,
                "head_sha": head_sha,
                "start_sha": start_sha,
                "position_type": "text",
                "old_path": file_path,
                "new_path": file_path,
                "new_line": int(line_number)
            }
        }

        headers = {**HEADERS, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=20)

        if response.status_code >= 400:
            return {"success": False, "status": response.status_code, "error": response.text}

        data = response.json()
        return {
            "success": True,
            "discussion_id": data.get("id"),
            "file": file_path,
            "line": line_number,
            "comment": comment
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
