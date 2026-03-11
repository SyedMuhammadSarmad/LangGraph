#without memmory
from langgraph.graph import StateGraph,END
from typing import TypedDict

class Agentstate(TypedDict):
    msg:str
    todo:list[str]

def add_todo(state:Agentstate)->Agentstate:
    state['todo'].append(state['msg'].replace("add ",""))
    return state

def show_todo(state:Agentstate)->Agentstate:
    print(state['todo'])
    return state

def router(state:Agentstate)->Agentstate:
    if "add" in state['msg']:
        return "add todo"
    else:
        return "show todo"

graph = StateGraph(Agentstate)

graph.add_node("router node",lambda state:state)
graph.add_node("add todo",add_todo)
graph.add_node("show todo",show_todo)

graph.set_entry_point("router node")
graph.add_conditional_edges("router node",router,
                            {
                                'add todo':'add todo',
                                'show todo':'show todo',
                            })
graph.add_edge('add todo',END)
graph.add_edge('show todo',END)

result = graph.compile()
output = result.invoke({
    "todo" : [],
    "msg" : "add buy eggs",
})
output2 = result.invoke({
    "todo" : [],
    "msg" : "add buy milk",
})

output3 = result.invoke({
    "todo" :[],
    "msg":"show todo"
})
print("final output",output3)

#with memmory
print("with memmory")
from langgraph.checkpoint.memory import MemorySaver

memmory = MemorySaver()

app2 = graph.compile(checkpointer=memmory)

config = {"configurable": { 
    "thread_id":"user_1"
}}

result = app2.invoke({"todo":[],"msg":"add buy milk"},config=config)

result2 = app2.invoke({"msg":"add buy butter"},config=config)

final_result = app2.invoke(
    {
        
        "msg":"show todo"
    },
    config = config
)

print(final_result)


