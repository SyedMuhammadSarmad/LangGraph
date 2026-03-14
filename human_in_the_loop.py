from langgraph.graph import StateGraph,END
from langgraph.graph import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from pprint import pprint

system_prompt = SystemMessage("""You are helpful assistant that check the weather of current city or use calculator to calculate result.
USE:                              
1. get_weather_tool to check weather of a particular city
2. calculator tool to do calculations check user input before calling calculator prompt user that divide by zero is not possible if user asks and donot call calculator tool.
    Also prompt the user if user input operator other than '+','-','*' or '/'
""")

load_dotenv()

memmory = MemorySaver()

llm = ChatOpenAI(model="gpt-4o-mini")

class AgentState(TypedDict):
    messages:Annotated[list,add_messages]

@tool
def get_weather(city:str)->str:
    '''
    this function accepts an arugument 'city' of type string and return weather of that 'city'
    '''
    return f"weather in {city} is sunny"

@tool 
def calculator(a:int,b:int,operator:str)->int:
    '''
    this is calculator tool use to accept two arguments a and b and operator('+' or '-' or '*' or '/') and returns the calculated answer
    '''
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    
    return a/b
    
    
llm_with_tools = llm.bind_tools([get_weather,calculator])
def llm_node(state:AgentState)->AgentState:
    resp = llm_with_tools.invoke([system_prompt]+state['messages'])
    return {
        "messages":[resp]
    }


graph = StateGraph(AgentState)

tool_node = ToolNode([get_weather,calculator])

graph.add_node('ai',llm_node)
graph.add_node('Tool node',tool_node)

graph.set_entry_point('ai')

def router(state:AgentState)->str:
    if len(state["messages"][-1].tool_calls)!=0:
        return "Tool node"
    else:
        return "end"

graph.add_conditional_edges('ai',router,
                            {
                                "Tool node":"Tool node",
                                "end":END
                            })

graph.add_edge("Tool node", "ai")

config = {
    "configurable":{
        "thread_id":"user_1"
    }
}

#human in the loop using interript before parameter
app = graph.compile(memmory,interrupt_before=["Tool node"])

# result1 = app.invoke({
#     "messages":["hello my name is sarmad"]
# }, config=config)

# result2 = app.invoke({
#     "messages":["what is my name?"]
# }, config=config)

result3 = app.invoke({
    "messages":["what is weather in karachi"]
}, config=config)

# result4 = app.invoke({
#     "messages":["what is two plus ninty"]
# }, config=config) 


print(result3["messages"][-1].content)

print(result3["messages"][-1].tool_calls)

input("tool is calling press any key to continue")

resume = app.invoke(None, config=config)

print(resume["messages"][-1].content)
