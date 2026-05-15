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

SYSTEM_PROMPT = "This is AI Agent for Git Review Process"


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
