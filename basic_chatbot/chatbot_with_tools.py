from typing import TypedDict, Annotated
from langchain.tools import tool
from langgraph.graph import add_messages, StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import pytz
from langchain_community.tools import TavilySearchResults, WikipediaQueryRun
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.utilities import WikipediaAPIWrapper
from firecrawl import scrape_with_selenium_tool
from langchain_core.prompts import ChatPromptTemplate
from weather_tool import get_weather_from_wttr_in
from finance import get_historical_stock_price, get_current_stock_price
import sqlite3
from datetime import datetime
import uuid
import os
import gradio as gr

# --- Tool Definitions ---
@tool
def get_current_datetime_tool(timezone: str = "UTC") -> str:
    """Return current date and time in a given timezone (e.g. 'Asia/Kolkata', 'UTC')."""
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    except pytz.UnknownTimeZoneError:
        return f"Error: Unknown timezone '{timezone}'."

# --- Setup ---
load_dotenv()

db_path = "checkpoints.sqlite"
if not os.path.exists(db_path):
    open(db_path, 'a').close()

conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# --- State Schema ---
class BasicState(TypedDict):
    messages: Annotated[list, add_messages]

# --- Tools ---
search_tool = TavilySearchResults()
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

tools = [
    search_tool,
    wiki_tool,
    scrape_with_selenium_tool,
    get_weather_from_wttr_in,
    get_historical_stock_price,
    get_current_stock_price,
    get_current_datetime_tool
]

# --- Prompt Template ---
base_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant with strong reasoning capabilities.
        The current date and time is: {current_datetime}.
        ALWAYS use tools for real-time or factual info."""
    ),
    ("placeholder", "{messages}")
])

# --- LLM ---
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')

# --- LangGraph Nodes ---
def chatbot(state: BasicState):
    current_datetime_utc = datetime.now(pytz.utc).strftime("%A, %B %d, %Y at %I:%M %p %Z UTC")
    llm_chain = (
        base_prompt.partial(current_datetime=current_datetime_utc)
        | llm.bind_tools(tools=tools)
    )
    return {'messages': llm_chain.invoke({"messages": state['messages']})}

def tool_route(state: BasicState):
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        return 'tool_node'
    return END

# --- LangGraph Setup ---
tool_node = ToolNode(tools=tools)
graph = StateGraph(BasicState)
graph.add_node('chatbot', chatbot)
graph.add_node('tool_node', tool_node)
graph.set_entry_point('chatbot')
graph.add_conditional_edges('chatbot', tool_route)
graph.add_edge('tool_node', 'chatbot')
langgraph_app = graph.compile(checkpointer=memory)

# --- Gradio Chat Function ---
def gradio_chat(user_input, history, thread_id):
    if not thread_id:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    try:
        events = langgraph_app.stream(
            {'messages': [HumanMessage(content=user_input)]},
            stream_mode="values",
            config=config
        )

        final_response = ""
        for event in events:
            if "messages" in event:
                last = event["messages"][-1]
                if hasattr(last, "content"):
                    final_response = ''.join(last.content) if isinstance(last.content, list) else str(last.content)

        history.append((user_input, final_response))
        return history, thread_id

    except Exception as e:
        history.append((user_input, "❌ Error: " + str(e)))
        return history, thread_id

# --- Gradio UI ---
with gr.Blocks(css=".footer, footer, .svelte-1ipelgc { display: none !important; }") as demo:
    gr.Markdown("## AI AGENT BOT")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask your question here...", label=None, lines=1)
    thread_id_state = gr.State()
    clear_btn = gr.Button("Clear")

    def clear_chat():
        return [], str(uuid.uuid4())

    msg.submit(gradio_chat, [msg, chatbot, thread_id_state], [chatbot, thread_id_state])
    clear_btn.click(clear_chat, [], [chatbot, thread_id_state])

# --- Run Gradio App ---
if __name__ == "__main__":
    demo.launch(share=False,show_api=False)

