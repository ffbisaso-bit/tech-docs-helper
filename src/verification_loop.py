from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from config import VERIFIER_MODEL, OPENAI_API_KEY
from hybrid_retrieval import hybrid_retrieve
from reranker import rerank_documents
from refine_retrieval import refine_context
from assess_evidence import assess_evidence
from confidence_gate import compute_confidence
from arbitrate_route import arbitrate_signals
from decision_engine import make_decision
from generate_answer import generate_answer


class VerificationReview(BaseModel):
    verdict: Literal["PASS", "RETRY_RETRIEVAL", "RETRY_GENERATION", "REFUSE", "ESCALATE"] = Field(
        description="Final verification verdict."
    )
    grounded: bool = Field(
        description="Whether the answer is supported by the evidence."
    )
    sufficient_evidence: bool = Field(
        description="Whether the evidence is strong enough to support answering."
    )
    reasoning: str = Field(
        description="Short explanation for the verdict."
    )


def format_context(documents: list) -> str:
    parts = []

    for i, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()
        parts.append(f"[Source {i}: {source}]\n{content}")

    return "\n\n".join(parts)


def verify_once(query: str, documents: list, answer: str) -> VerificationReview:
    context = format_context(documents)

    verifier = ChatOpenAI(
        model=VERIFIER_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0
    ).with_structured_output(VerificationReview, method="json_schema")

    prompt = f"""
You are the verification layer of a controlled AI system.

Your job is to review:
1. the user query
2. the retrieved evidence
3. the generated answer

You must decide exactly one verdict:

PASS
- Use when the answer is fully grounded in the evidence and the evidence is sufficient.
- Return PASS only when the answer stays within what the evidence directly supports.

RETRY_RETRIEVAL
- Use when the answer may be reasonable, but the evidence is too weak, too narrow, incomplete, or missing key support.
- This means the system should collect more evidence and try again.

RETRY_GENERATION
- Use when the evidence is sufficient, but the answer itself is poorly written, overly broad, loosely grounded, or includes unnecessary wording that is not directly supported.

REFUSE
- Use when the evidence does not support answering the query.

ESCALATE
- Use when the case is ambiguous, conflicting, risky, or unsafe for automatic answering.

Rules:
- Prefer PASS only when the answer is clearly and directly supported by the evidence.
- If any part of the answer is not directly supported by the evidence, do not return PASS.
- Do not approve answers that add interpretation, speculation, assumptions, or unsupported qualifiers.
- If the evidence is not sufficient to support a reliable answer, choose RETRY_RETRIEVAL, REFUSE, or ESCALATE as appropriate.
- Be strict.
- Keep reasoning brief.

User query:
{query}

Evidence:
{context}

Generated answer:
{answer}
"""
    review = verifier.invoke(prompt)
    return review


def run_verification_loop(
    query: str,
    vector_store,
    chunks: list,
    decision: dict,
    max_retries: int = 2
) -> dict:
    if decision["decision"] == "REFUSE":
        return {
            "final_decision": "REFUSE",
            "final_answer": "I cannot answer because the evidence is insufficient.",
            "attempts": 0,
            "verification": {
                "verdict": "REFUSE",
                "grounded": False,
                "sufficient_evidence": False,
                "reasoning": "Decision engine refused before generation."
            },
            "documents": []
        }

    if decision["decision"] == "ESCALATE":
        return {
            "final_decision": "ESCALATE",
            "final_answer": "This case should be escalated for review.",
            "attempts": 0,
            "verification": {
                "verdict": "ESCALATE",
                "grounded": False,
                "sufficient_evidence": False,
                "reasoning": "Decision engine escalated before generation."
            },
            "documents": []
        }

    retrieval_sizes = [5, 8, 12]
    attempt = 0
    last_review = None
    final_docs = []

    while attempt <= max_retries:
        k = retrieval_sizes[min(attempt, len(retrieval_sizes) - 1)]

        retrieved_docs = hybrid_retrieve(
            query=query,
            vector_store=vector_store,
            documents=chunks,
            dense_k=k,
            lexical_k=k
        )

        reranked_docs = rerank_documents(query, retrieved_docs)
        refined_docs = refine_context(reranked_docs, max_chunks=3)

        evidence_result = assess_evidence(query, refined_docs)
        confidence_result = compute_confidence(evidence_result)
        arbitration_result = arbitrate_signals(evidence_result, confidence_result)
        refreshed_decision = make_decision(
            evidence_result,
            confidence_result,
            arbitration_result
        )

        if refreshed_decision["decision"] != "ANSWER":
            return {
                "final_decision": refreshed_decision["decision"],
                "final_answer": (
                    "I cannot answer because the evidence is insufficient."
                    if refreshed_decision["decision"] == "REFUSE"
                    else "This case should be escalated for review."
                ),
                "attempts": attempt,
                "verification": {
                    "verdict": refreshed_decision["decision"],
                    "grounded": False,
                    "sufficient_evidence": evidence_result["enough_evidence"],
                    "reasoning": "Decision engine blocked answering during verification loop."
                },
                "documents": refined_docs
            }

        answer = generate_answer(query, refined_docs, refreshed_decision)
        review = verify_once(query, refined_docs, answer)

        last_review = review
        final_docs = refined_docs

        if review.verdict == "PASS":
            return {
                "final_decision": "ANSWER",
                "final_answer": answer,
                "attempts": attempt + 1,
                "verification": review.model_dump(),
                "documents": refined_docs
            }

        if review.verdict == "RETRY_RETRIEVAL":
            attempt += 1
            continue

        if review.verdict == "RETRY_GENERATION":
            answer = generate_answer(query, refined_docs, refreshed_decision)
            review = verify_once(query, refined_docs, answer)

            last_review = review
            final_docs = refined_docs

            if review.verdict == "PASS":
                return {
                    "final_decision": "ANSWER",
                    "final_answer": answer,
                    "attempts": attempt + 1,
                    "verification": review.model_dump(),
                    "documents": refined_docs
                }

            attempt += 1
            continue

        if review.verdict == "REFUSE":
            return {
                "final_decision": "REFUSE",
                "final_answer": "I cannot answer because the evidence is insufficient.",
                "attempts": attempt + 1,
                "verification": review.model_dump(),
                "documents": refined_docs
            }

        if review.verdict == "ESCALATE":
            return {
                "final_decision": "ESCALATE",
                "final_answer": "This case should be escalated for review.",
                "attempts": attempt + 1,
                "verification": review.model_dump(),
                "documents": refined_docs
            }

        attempt += 1

    fallback_decision = "ESCALATE"
    if last_review and last_review.verdict == "REFUSE":
        fallback_decision = "REFUSE"

    fallback_answer = (
        "I cannot answer because the evidence is insufficient."
        if fallback_decision == "REFUSE"
        else "This case should be escalated for review."
    )

    return {
        "final_decision": fallback_decision,
        "final_answer": fallback_answer,
        "attempts": max_retries + 1,
        "verification": last_review.model_dump() if last_review else {
            "verdict": fallback_decision,
            "grounded": False,
            "sufficient_evidence": False,
            "reasoning": "Verification loop ended without a passing answer."
        },
        "documents": final_docs
    }