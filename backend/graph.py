from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages 
from pydantic import BaseModel, Field
from langchain.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
import requests 
from backend.rag import rag_tool
from dotenv import load_dotenv
load_dotenv()

model= ChatGroq(
    model= 'qwen/qwen3.6-27b',
    )



class BotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# tools 
search_tools= DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str)-> dict:
    """
    Performs the basic arithmatic operations on two numbers
    Supported operations: add, sub, multiply, div
    """
    
    try: 
        if operation=="add" or operation=="+":
            result= first_num + second_num
        elif(operation=="sub" or operation=="-"):
            result= first_num - second_num
        elif(operation=="multiply" or operation=="*"):
            result= first_num * second_num
        elif(operation=="div" or operation=="/"):
            if(second_num==0):   return {'error':'Division by zero is not allowed.'}
            result= first_num / second_num
        else:
            return {'error':f'unsupported operation {operation}'}
        return {'first_num':first_num, 'second_num': second_num, 'operation':operation, 'result':result}
    except Exception as e:
        return {'error': str(e)}       
    
@tool
def get_stock_price(symbol:str)-> dict:
    """
    Fetch latest stock price for a given symbol (e.g 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=XOVS4K71WJRBEVSU'
    r = requests.get(url)
    data = r.json()
    return data    


tools = [search_tools, get_stock_price, calculator, rag_tool]
llm_with_tools = model.bind_tools(tools)



def chat_node(state: BotState, config=None)-> BotState:
    """
    LLM node that may answer or request a tool call
    """
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
            "You are a helpful assistant. For questions about the uploaded PDF, call "
            "the `rag_tool` and include the thread_id "
            f"`{thread_id}`. You can also use the web search, stock price, and "
            "calculator tools when helpful. If no document is available, ask the user "
            "to upload a PDF."
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}

tool_node= ToolNode(tools)

class HeadingSchema(BaseModel):
    heading: str= Field(description="Short title ONLY. Max 6 words. No punctuation, no extra text.")
headingbot= model.with_structured_output(HeadingSchema)

graph= StateGraph(BotState)
conn= sqlite3.connect("comeonchat.db", check_same_thread=False)
checkpointer= SqliteSaver(conn=conn)

graph.add_node('chat_node', chat_node)
graph.add_node('tools', tool_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('tools', 'chat_node')
graph.add_conditional_edges('chat_node', tools_condition)
bot= graph.compile(checkpointer=checkpointer)
