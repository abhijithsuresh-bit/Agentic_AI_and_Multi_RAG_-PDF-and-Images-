from typing import Annotated
from langchain_core import tools
from typing_extensions import TypedDict
from langgraph.graph import START , END
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
import os
from dotenv import load_dotenv
load_dotenv()

# we are converting our langgraph agent to cloud with the help of langgraph cli

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "test_project"

from langchain.chat_models import init_chat_model

llm = init_chat_model(model="groq:openai/gpt-oss-120b")

class State(TypedDict):
    # baseMessage shows the structure of the message
    messages: Annotated[list[BaseMessage] , add_messages]

# Graph with a tool call
from langgraph.prebuilt import ToolNode
from langchain.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# we only have 1 tool
tools = [add]
# we convvert this tool to a node 
tool_node = ToolNode(tools)

llm_with_tools  = llm.bind_tools(tools)

def call_llm_model(state: State):
    return llm_with_tools.invoke(state["messages"])


from langgraph.graph import StateGraph , START , END
from langgraph.prebuilt import ToolNode , tools_condition


builder  = StateGraph(State)
builder.add_node("tool_calling_llm", call_llm_model)
builder.add_node("tools", tool_node)

# add edges

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    # if the moodel knows an answer it will directly go to the end if not it will go to the toool
    "tool_calling_llm",
    tools_condition
)
# if the model goes to the tool nodel we need to stop
builder.add_edge("tools" , END )

graph = builder.compile()





#this is our json file which is imp
#{
#    "dependencies":["."],
#    "graph":{
#        "tool_agent":"agentic.py:tool_agent" here we need to provide thie file path if its in a file ./agentic.py:tool_agent   tool_agent is the name 
#    },
#    "env":"../.env"
#}

# if our configuration file is in a folder 
# before running open cmd change the folder to the one where the configuration file is present and then run the command
# run: langgraph dev