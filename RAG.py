import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ")
google_api_key = os.getenv("GOOGLE_API_KEY")

# Set the environment variable for Google API explicitly (needed for Langchain)
os.environ["GOOGLE_API_KEY"] = google_api_key

# UI Title
st.title("📄 PDF Chat with Gemma (RAG)")

# Upload a single PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save uploaded PDF temporarily
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load PDF and process
    loader = PyPDFLoader("temp_uploaded.pdf")
    docs = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    # Create vectorstore using GoogleEmbeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=google_api_key
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Initialize retriever
    retriever = vectorstore.as_retriever()

    # Load Gemma model from Groq
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

    # Set up the RAG prompt
    prompt = ChatPromptTemplate.from_template("""
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    </context>
    Question: {input}
    """)

    # Create chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # Input for question
    question = st.text_input("Ask a question based on the uploaded PDF:")

    if question:
        with st.spinner("Generating answer..."):
            start = time.process_time()
            response = retrieval_chain.invoke({"input": question})
            st.write("🧠 **Answer:**", response["answer"])
            st.caption(f"⏱️ Response time: {round(time.process_time() - start, 2)} sec")

            # Show context if user wants
            with st.expander("📄 Document Chunks Used"):
                for i, doc in enumerate(response["context"]):
                    st.markdown(f"**Chunk {i + 1}:**")
                    st.write(doc.page_content)
                    st.write("---")

else:
    st.info("Upload a PDF to get started.")
