from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

generate_prompt=ChatPromptTemplate.from_messages(
    [
        (
            'system',
            'You are twitter influencer techie assistant tasked with writing excellent tweets'
            'Generate the best possible tweets based on the user_requests.'
            'if the user provides critique,respond with a revised and better version of your previous attempts.'
            'Give the tweets without options in a best possible way',
        ),
        MessagesPlaceholder(variable_name='messages'),
    ]
)

reflection_prompt=ChatPromptTemplate.from_messages(
    [
        (
            'system',
            'you are a viral twitter influencer grading a tweet.Generate critique recommendations for the users tweets'
            'Always provide a detailed recommendations,including requests for length and virality,style,etc.,.',

        ),MessagesPlaceholder(variable_name='messages')
    ]
)

llm=ChatGoogleGenerativeAI(model='gemini-1.5-flash')

generate_chain=generate_prompt|llm
reflection_chain=reflection_prompt|llm
