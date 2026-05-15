import config  # load .env first

from langchain_core.messages import HumanMessage
from langgraph.graph import START, END, StateGraph

from graph.state import AgentState
from graph.nodes import git_process, use_tool_or_agent, tool_node


def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("call", git_process)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "call")
    graph.add_conditional_edges(
        "call",
        use_tool_or_agent,
        {"end": END, "continue": "tools"}
    )
    graph.add_edge("tools", "call")

    return graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def main():
    agent = build_agent()

    print(agent.get_graph().draw_mermaid())

    conversation_history = []
    user_input = input("How can I help you ??::")
    conversation_history.append(HumanMessage(content=user_input))

    print_stream(
        agent.stream({"messages": conversation_history}, stream_mode="values")
    )


if __name__ == "__main__":
    main()
