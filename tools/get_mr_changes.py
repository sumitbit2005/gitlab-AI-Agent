import re
import urllib.parse
import requests
from langchain_core.tools import tool
from config import GITLAB_URL, HEADERS


def annotate_diff(diff_text):
    """
    Parse a unified diff and annotate each line with its new_line number.
    Returns a string where each line is prefixed with its line number.
    This helps the LLM pick correct line numbers for inline comments.
    """
    if not diff_text:
        return diff_text

    lines = diff_text.split("\n")
    annotated = []
    new_line_num = 0

    for line in lines:
        # Parse hunk header: @@ -old_start,count +new_start,count @@
        hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk_match:
            new_line_num = int(hunk_match.group(1))
            annotated.append(line)
            continue

        if line.startswith("-"):
            # Deleted line — no new_line number
            annotated.append(f"     | -{line[1:]}")
        elif line.startswith("+"):
            # Added line — has a new_line number
            annotated.append(f"{new_line_num:4d} | +{line[1:]}")
            new_line_num += 1
        else:
            # Context line — has a new_line number
            annotated.append(f"{new_line_num:4d} |  {line}")
            new_line_num += 1

    return "\n".join(annotated)


@tool
def get_mr_changes(project: str, mr_no: int):
    """
    Fetch GitLab Merge Request Changes with annotated line numbers.

    Each diff line is prefixed with its new_line number so you can
    use it directly in add_inline_comment. Lines starting with a
    number are commentable. Lines without a number (deleted lines)
    are not commentable.

    Args:
        project: GitLab project path. Example: mygroup/myrepo
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
                    "diff": annotate_diff(change.get("diff")),
                }
                for change in data.get("changes", [])
            ]
        }

    except Exception as e:
        return {"error": str(e)}
