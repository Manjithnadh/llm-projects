from transformers import pipeline

summarizer=pipeline('summarization',model='facebook/bart-large-cnn')

def summarize_text(text):

    summary=summarizer(text,max_length=150,min_length=50,do_sample=False)
    return(summary[0]['summary_text'])


sample_text = """
    Hugging Face is a company that provides a user-friendly library for natural language processing tasks. 
    It focuses on democratizing artificial intelligence by making machine learning models more accessible and easy to use.
    Their mission is to create a world where anyone can use and deploy AI models, regardless of their technical expertise. 
    Hugging Face is also known for its large collection of pre-trained models available to the public, covering a wide variety of NLP tasks such as text generation, translation, summarization, question-answering, and more.
"""


