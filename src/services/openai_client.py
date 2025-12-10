"""
OpenAI client initialization and caching
"""
import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


@st.cache_resource
def get_openai_client():
    """Get cached OpenAI client"""
    return OpenAI()


@st.cache_resource
def get_llm():
    """Get cached LangChain LLM"""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.4)


@st.cache_resource
def get_embeddings():
    """Get cached OpenAI embeddings"""
    return OpenAIEmbeddings()

