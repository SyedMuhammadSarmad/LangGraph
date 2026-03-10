from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list[str]
    step: int

def node_a(state: AgentState) -> AgentState:
    print("Node A running")
    state["messages"].append("A was here")
    state["step"] += 1
    return state

def node_b(state: AgentState) -> AgentState:
    print("Node B running")
    state["messages"].append("B was here")
    return state

def node_c(state:AgentState) -> AgentState:
    print("Node C running")
    state["messages"].append("C was here")
    return state

def route(state:AgentState) -> str:
    if state["step"] < 1:
        return "node_b"
    else:
        return "node_c"


graph = StateGraph(AgentState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)

graph.set_entry_point("node_a")
graph.add_conditional_edges("node_a",
                            route,
                            {
                                "node_b":"node_b",
                                "node_c":"node_c"
                            })
graph.add_edge("node_b",END)
graph.add_edge("node_c",END)
app = graph.compile()
result = app.invoke({"messages": [], "step": 0})
print(result)