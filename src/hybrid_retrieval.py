from typing import List
from langchain_core.documents import Document


def lexical_search(query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
    query_words = set(query.lower().split())

    scored_docs = []

    for doc in documents:
        content_words = set(doc.page_content.lower().split())
        overlap = len(query_words.intersection(content_words))

        if overlap > 0:
            scored_docs.append((doc, overlap))

    # sort by overlap (descending)
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in scored_docs[:top_k]]


def hybrid_retrieve(
    query: str,
    vector_store,
    documents: List[Document],
    dense_k: int = 5,
    lexical_k: int = 5
) -> List[Document]:

    # Dense retrieval (semantic)
    dense_results = vector_store.similarity_search(query, k=dense_k)

    # Lexical retrieval (keyword overlap)
    lexical_results = lexical_search(query, documents, top_k=lexical_k)

    # Merge results
    combined = dense_results + lexical_results

    # Deduplicate (by content)
    seen = set()
    unique_docs = []

    for doc in combined:
        key = doc.page_content.strip()

        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs