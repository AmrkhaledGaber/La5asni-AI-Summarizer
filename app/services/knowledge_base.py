from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# 🔹 إعداد الـ Embeddings و Chroma DB
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./vector_db", embedding_function=embedding_model)

# 🔹 إعداد LLM Gemini
import os
from dotenv import load_dotenv
load_dotenv()
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

def retrieve_context(query: str, k: int = 5) -> list:
    """
    تسترجع أفضل k نصوص مشابهة من الـ Knowledge Base.
    """
    docs = vector_db.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]

def enrich_with_rag(query: str, num_pages: int, useful_ratio: float) -> dict:
    """
    يدمج بين الـ RAG والـ LLM (Gemini) لتحليل الملف التدريبي.
    """
    context = retrieve_context(query)
    context_str = "\n".join(context)

    prompt = PromptTemplate.from_template("""
You are an expert instructional designer.

Use the following **context** to assist in analyzing the training document:

Context:
{context}

Document:
{query}

Return a valid JSON in this format:

{{
  "summary": "...",
  "key_points": [...],
  "training_modules": [
    {{"title": "...", "description": "...", "estimated_minutes": 30}}
  ],
  "num_pages": {num_pages},
  "useful_text_ratio": {useful_ratio},
  "num_key_points": ...
}}
    """)

    parser = JsonOutputParser()
    chain = prompt | gemini_llm | parser

    return chain.invoke({
        "query": query,
        "context": context_str,
        "num_pages": num_pages,
        "useful_ratio": useful_ratio
    })
