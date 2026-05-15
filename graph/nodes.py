import httpx
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from config import OPENAI_MODEL, OPENAI_API_KEY
from tools import tools
from graph.state import AgentState


http_client = httpx.Client(verify=False)
model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client
).bind_tools(tools)

tool_node = ToolNode(tools=tools)

SYSTEM_PROMPT = """
    You are an expert GitLab code reviewer.

When reviewing Merge Requests:

1. First fetch MR details (to get diff_refs) and MR changes (to get diffs).
2. If diffs are small or ambiguous, retrieve full file context.
3. Analyze for: bugs, performance, security, CI/CD risks, config errors.
4. For each specific issue found on a code line, post an inline comment
   using add_inline_comment with the exact file_path and new_line from the diff.
   Use diff_refs (base_sha, head_sha, start_sha) from the MR details.
5. After all inline comments are posted, post a summary comment using
   add_mr_comment with an overall review of the MR.
6. Line numbers come from diff hunk headers: @@ -old_start,count +new_start,count @@
   Count from new_start to find the exact new_line for added/modified lines.
"""


def git_process(state: AgentState) -> AgentState:
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    response = model.invoke([system_message] + list(state["messages"]))
    return {"messages": [response]}


def use_tool_or_agent(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    else:
        return "end"
