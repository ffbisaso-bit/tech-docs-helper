from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from config import CHAT_MODEL, OPENAI_API_KEY

_llm = ChatOpenAI(
    model=CHAT_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0
)


class QueryRewriteResult(BaseModel):
    original_query: str = Field(description="The original user query, unchanged.")
    rewritten_query: str = Field(
        description=(
            "A retrieval-optimised rewrite that preserves the user's exact intent and domain. "
            "Must equal the original query if needs_clarification is true."
        )
    )
    needs_clarification: bool = Field(
        description=(
            "True only if the query is so vague or ambiguous that any rewrite would risk "
            "changing the user's intent. False if the intent is reasonably clear."
        )
    )
    clarification_reason: str = Field(
        description=(
            "A brief explanation of why clarification is needed. "
            "Must be an empty string if needs_clarification is false."
        )
    )


_structured_llm = _llm.with_structured_output(QueryRewriteResult)

REWRITE_PROMPT = """You are the query rewriting layer of a controlled retrieval system.

Your job is to decide whether to rewrite the query or request clarification — never both, never neither.

═══════════════════════════════════════
STEP 1 — ASSESS INTENT CLARITY
═══════════════════════════════════════
Ask: Can I state with confidence what information the user is trying to retrieve?

Set needs_clarification = true ONLY if:
- The query contains no recoverable intent (e.g. "the thing we discussed", "that error")
- Multiple interpretations exist that would lead to fundamentally different retrievals
- A critical entity or subject is missing and cannot be reasonably inferred

Do NOT set needs_clarification = true if:
- The query is short but clear (e.g. "refund policy", "how do I reset my password")
- The query uses generic references ("the system", "the service") but the action/topic is clear
- The query describes a symptom or problem clearly, even if the cause is unknown
- You could improve the phrasing without changing the meaning

═══════════════════════════════════════
STEP 2A — IF needs_clarification = true
═══════════════════════════════════════
- Set rewritten_query = original query (unchanged)
- Set clarification_reason = one sentence explaining exactly what is missing or ambiguous
- Do not attempt a rewrite

═══════════════════════════════════════
STEP 2B — IF needs_clarification = false
═══════════════════════════════════════
Rewrite the query for retrieval accuracy. Rules:
- Preserve the user's intent exactly — do not broaden or narrow it
- Preserve the original domain exactly
- Do not introduce entities, technologies, causes, or assumptions not clearly implied
- Expand implicit references only if the meaning is unambiguous
- Make the query more explicit and retrieval-friendly
- If the query is already optimal, keep the rewrite very close to the original
- Set clarification_reason = "" (empty string)

═══════════════════════════════════════
ABSOLUTE CONSTRAINTS
═══════════════════════════════════════
- Do not answer the question
- Do not add commentary
- original_query must always equal the user's input, unchanged

User query:
{user_query}
"""


def rewrite_query(user_query: str) -> QueryRewriteResult:
    clean_query = user_query.strip()

    if not clean_query:
        return QueryRewriteResult(
            original_query="",
            rewritten_query="",
            needs_clarification=True,
            clarification_reason="Query is empty. Please provide a question or topic."
        )

    result: QueryRewriteResult = _structured_llm.invoke(
        REWRITE_PROMPT.format(user_query=clean_query)
    )

    if result.needs_clarification:
        result.rewritten_query = clean_query
    else:
        result.clarification_reason = ""

    result.original_query = clean_query

    return result