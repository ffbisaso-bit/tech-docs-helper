import re
from langchain_core.documents import Document


STOP_WORDS = {
    "what", "is", "the", "a", "an", "does", "do", "did",
    "when", "where", "why", "how", "of", "in", "on", "at",
    "to", "for", "by", "with", "and", "or"
}


def normalize_word(word: str) -> str:
    word = word.lower()

    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"

    if word.endswith("es") and len(word) > 3:
        return word[:-2]

    if word.endswith("s") and len(word) > 3:
        return word[:-1]

    if word.endswith("ed") and len(word) > 4:
        return word[:-2]

    return word


def extract_normalized_words(text: str) -> set[str]:
    words = re.findall(r"\w+", text.lower())
    normalized = {normalize_word(word) for word in words}
    return {word for word in normalized if word not in STOP_WORDS}


def assess_evidence(query: str, documents: list[Document]) -> dict:
    query_words = extract_normalized_words(query)
    query_text = query.lower()

    if not documents:
        return {
            "enough_evidence": False,
            "total_chunks": 0,
            "average_overlap": 0,
            "strong_chunks": 0,
            "useful_chunks": 0,
            "reason": "No documents retrieved."
        }

    overlap_scores = []
    strong_chunks = 0
    useful_chunks = 0

    for doc in documents:
        content = doc.page_content.lower()
        doc_words = extract_normalized_words(content)

        # 1. Keyword overlap
        overlap = len(query_words.intersection(doc_words))

        # 2. Phrase match boost (important)
        phrase_match = any(q in content for q in query_words)

        # 3. Partial match boost
        partial_match = any(
            q in word or word in q
            for q in query_words
            for word in doc_words
        )

        score = overlap

        if phrase_match:
            score += 1

        if partial_match:
            score += 1

        overlap_scores.append(score)

        # classify chunk strength
        if score >= 3:
            strong_chunks += 1
        elif score >= 1:
            useful_chunks += 1

    average_overlap = sum(overlap_scores) / len(overlap_scores)

    enough_evidence = strong_chunks >= 1 and (strong_chunks + useful_chunks) >= 2

    return {
        "enough_evidence": enough_evidence,
        "total_chunks": len(documents),
        "average_overlap": average_overlap,
        "strong_chunks": strong_chunks,
        "useful_chunks": useful_chunks,
        "reason": "Evidence looks sufficient." if enough_evidence else "Evidence is weak."
    }