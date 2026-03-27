import re
from langchain_core.documents import Document


def rerank_documents(query: str, documents: list[Document]) -> list[Document]:
    query_words = set(re.findall(r"\w+", query.lower()))

    scored_documents = []

    for doc in documents:
        doc_words = set(re.findall(r"\w+", doc.page_content.lower()))
        score = len(query_words.intersection(doc_words))
        scored_documents.append((score, doc))

    scored_documents.sort(key=lambda item: item[0], reverse=True)

    reranked_docs = [doc for score, doc in scored_documents]
    return reranked_docs