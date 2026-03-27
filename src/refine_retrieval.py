from langchain_core.documents import Document


def refine_context(documents: list[Document], max_chunks: int = 3) -> list[Document]:
    refined_docs = []
    seen_content = set()

    for doc in documents:
        content = doc.page_content.strip()

        if not content:
            continue

        if content in seen_content:
            continue

        seen_content.add(content)
        refined_docs.append(doc)

        if len(refined_docs) >= max_chunks:
            break

    return refined_docs