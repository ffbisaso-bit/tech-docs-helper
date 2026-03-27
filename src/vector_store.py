from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import OPENAI_API_KEY, EMBEDDING_MODEL


def build_vector_store(chunks: list[Document]) -> FAISS:
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY
    )

    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store