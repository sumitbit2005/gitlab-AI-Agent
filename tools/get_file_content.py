import urllib.parse
import requests
from langchain_core.tools import tool
from config import GITLAB_URL, HEADERS
import re



def mask_sensitive(content: str) -> str:
    """
    Mask secrets/tokens/passwords.
    """

    patterns = [
        r"(password\s*[:=]\s*)(.+)",
        r"(secret\s*[:=]\s*)(.+)",
        r"(token\s*[:=]\s*)(.+)",
        r"(api[_-]?key\s*[:=]\s*)(.+)",
        r"(secret_args\s*=\s*)(.+)"
    ]

    for pattern in patterns:
        content = re.sub(
            pattern,
            r"\1********",
            content,
            flags=re.IGNORECASE
        )

    return content



@tool
def get_file_content(project: str, file_path: str, branch : str = "main", max_lines: int = 200):
    """
    Retrieve contextual file content from GitLab.
    Use this tool when reviewing Merge Requests if:
    - diff lacks sufficient context
    - surrounding code is needed
    - imports/classes/config context matters
    - configuration files (.gitlab-ci.yml, yaml, json) need validation

    Helpful for deeper code review.
    
    """
    try:
        encoded_project = urllib.parse.quote_plus(project)
        encoded_file = urllib.parse.quote_plus(file_path)

        url = (
            f"{GITLAB_URL}/api/v4/projects/"
            f"{encoded_project}/repository/files/"
            f"{encoded_file}/raw"
            f"?ref={branch}"
        )

        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.text
        content = mask_sensitive(data)
        lines = content.splitlines()

        total_lines = len(lines)

        truncated = False

        if total_lines > max_lines:
            lines = lines[:max_lines]
            truncated = True

        content = "\n".join(lines)

        return {

            "file": file_path,

            "branch": branch,

            "total_lines":
                total_lines,

            "returned_lines":
                len(lines),

            "truncated":
                truncated,

            "content":
                content
        }


    except Exception as e:
        return {"error": str(e)}
