from langchain_openai import ChatOpenAI

from config import CHAT_MODEL, OPENAI_API_KEY


def format_context(documents: list) -> str:
    parts = []

    for i, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()
        parts.append(f"[Source {i}: {source}]\n{content}")

    return "\n\n".join(parts)


def generate_answer(query: str, documents: list, decision: dict) -> str:
    final_decision = decision["decision"]

    if final_decision == "REFUSE":
        return "I cannot answer because the evidence is insufficient."

    if final_decision == "ESCALATE":
        return "This case should be escalated for review."

    context = format_context(documents)

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0
    )



    prompt = f"""
You are a technical documentation assistant.

Answer the user's question using only the evidence below.

Strict rules:
- Use only facts explicitly supported by the evidence.
- Do not add interpretations, summaries, or extra qualifiers.
- Do not use words that are not necessary.
- Keep the answer to 2 sentences maximum.
- If the answer is not fully supported by the context, say: "The evidence is not sufficient to answer fully."

User question:
{query}

Evidence:
{context}
"""

    response = llm.invoke(prompt)
    return response.content