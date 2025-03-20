import streamlit as st
import app

from app import summarize_text



def main():
    st.title('text summarization tool')
    st.markdown('enter text below which is to be summarized')

    text_input=st.text_area('paste your text:','')

    if st.button('summarize'):
        if text_input:
            summary=summarize_text(text_input)
            st.subheader('summary')
            st.write(summary)
        else:
            st.warning('please enter a text to summarize')

if __name__=='__main__':
    main()