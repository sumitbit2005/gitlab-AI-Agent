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
                     For added lines (+), use the new_line number from the diff.
                     Calculate: hunk header shows @@ -old,count +NEW_START,count @@
                     The first line shown is NEW_START, count down for each line.
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

        line_number = int(line_number)

        # Try the exact line and nearby lines (+/- 1) to handle off-by-one from LLM
        attempts = [
            {"new_line": line_number},
            {"new_line": line_number - 1},
            {"new_line": line_number + 1},
            {"old_line": line_number},
            {"old_line": line_number - 1},
        ]

        last_error = None
        for line_param in attempts:
            payload = {
                "body": comment,
                "position": {
                    "base_sha": base_sha,
                    "head_sha": head_sha,
                    "start_sha": start_sha,
                    "position_type": "text",
                    "old_path": file_path,
                    "new_path": file_path,
                    **line_param
                }
            }

            headers = {**HEADERS, "Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "discussion_id": data.get("id"),
                    "file": file_path,
                    "line": line_param,
                    "comment": comment
                }
            last_error = response.text

        return {"success": False, "status": 400, "error": last_error}

    except Exception as e:
        return {"success": False, "error": str(e)}
