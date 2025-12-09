import os
import streamlit as st
from pypdf import PdfReader

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()


class vectorStore:

    @staticmethod
    def load_pdf_text(pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        full_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        return full_text

    @staticmethod
    @st.cache_resource(show_spinner=True)
    def get_vectorstore(pdf_path: str, base_chroma_dir: str):
        """
        Loads or builds a unique Chroma vectorstore for each PDF.

        Example:
        pdf_path = "./books/the_lost_symbol.pdf"
        base_chroma_dir = "./chroma_stores"
        Final directory = "./chroma_stores/the_lost_symbol"
        """

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found at {pdf_path}")

        # Create unique directory name from PDF name
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        chroma_dir = os.path.join(base_chroma_dir, pdf_name)

        os.makedirs(chroma_dir, exist_ok=True)

        # Load full text
        full_text = vectorStore.load_pdf_text(pdf_path)

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
        )
        docs = splitter.create_documents([full_text])

        # Build / load vector store
        db = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory=chroma_dir
        )

        return db
