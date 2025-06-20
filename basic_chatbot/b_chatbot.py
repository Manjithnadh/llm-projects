from typing import TypedDict,Annotated
from langgraph.graph import add_messages,StateGraph,END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage,HumanMessage
from dotenv import load_dotenv


load_dotenv()

llm=ChatGoogleGenerativeAI(model='gemini-1.5-flash')


class BasicState(TypedDict):
    messages: Annotated[list,add_messages]

def chatbot(state:BasicState):
    return {
        'messages':llm.invoke(state['messages'])
    }

graph=StateGraph(BasicState)

graph.add_node('chatbot',chatbot)
graph.set_entry_point('chatbot')
graph.add_edge('chatbot',END)

app=graph.compile()

while True:
    user_input=input('user: ')
    if user_input in ['end', 'exit']:
        break
    else:
        result=app.invoke({
            'messages':[HumanMessage(content=user_input)]
        })

        print(result)
