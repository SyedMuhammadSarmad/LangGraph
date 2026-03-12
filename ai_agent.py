from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from typing import Annotated,TypedDict

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI()

memmory = MemorySaver()

class AgentState(TypedDict):
    msgs:Annotated[list,add_messages]

def llm_node(state:AgentState) -> AgentState:
    response = llm.invoke(state['msgs'])
    return {
        "msgs":[response]
    }

graph = StateGraph(AgentState)

graph.add_node("ai node",llm_node)

graph.set_entry_point("ai node")
graph.add_edge("ai node",END)

app = graph.compile(memmory)

config = {
    "configurable":
    {
        "thread_id":"user_1"
    }
}

print(
    app.invoke(
        {"msgs":["hello my name is sarmad"]},
        config=config
    )["msgs"][-1].content
)

print(
    app.invoke(
        {"msgs":["whats my name"]},
        config=config
    )["msgs"][-1].content
)