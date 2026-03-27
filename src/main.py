from loader import load_text_documents, chunk_documents
from vector_store import build_vector_store
from rewrite_query import rewrite_query
from hybrid_retrieval import hybrid_retrieve
from reranker import rerank_documents
from refine_retrieval import refine_context
from assess_evidence import assess_evidence
from confidence_gate import compute_confidence
from arbitrate_route import arbitrate_signals
from decision_engine import make_decision
from verification_loop import run_verification_loop
from audit_log import write_audit_log
from drift_detection import run_drift_detection


def main():
    documents = load_text_documents()
    chunks = chunk_documents(documents)
    vector_store = build_vector_store(chunks)

    query = "When do health checks run?"
    rewrite_result = rewrite_query(query)

    if rewrite_result.needs_clarification:
        audit_data = {
            "original_query": rewrite_result.original_query,
            "rewritten_query": rewrite_result.rewritten_query,
            "needs_clarification": rewrite_result.needs_clarification,
            "clarification_reason": rewrite_result.clarification_reason,
            "initial_evidence": {},
            "initial_confidence": {},
            "initial_arbitration": {},
            "initial_decision": {"decision": "ESCALATE", "reason": "Clarification required before retrieval."},
            "verification_result": {
                "verdict": "ESCALATE",
                "grounded": False,
                "sufficient_evidence": False,
                "reasoning": "Query rewriting layer determined clarification is required."
            },
            "final_decision": "ESCALATE",
            "attempts": 0,
            "final_answer": f"Clarification needed: {rewrite_result.clarification_reason}",
            "sources": []
        }

        log_path = write_audit_log(audit_data)
        drift_result = run_drift_detection()

        print("ORIGINAL QUERY:", rewrite_result.original_query)
        print("\nREWRITTEN QUERY:")
        print(rewrite_result.rewritten_query)
        print("\nNEEDS CLARIFICATION:")
        print(rewrite_result.needs_clarification)
        print("\nCLARIFICATION REASON:")
        print(rewrite_result.clarification_reason)
        print("\nFINAL DECISION:")
        print("ESCALATE")
        print("\nFINAL ANSWER:")
        print(f"Clarification needed: {rewrite_result.clarification_reason}")
        print("\nAUDIT LOG:")
        print(log_path)
        print("\nDRIFT DETECTION:")
        print(drift_result)
        return

    retrieval_query = rewrite_result.rewritten_query

    initial_retrieved_docs = hybrid_retrieve(
        query=retrieval_query,
        vector_store=vector_store,
        documents=chunks,
        dense_k=5,
        lexical_k=5
    )

    initial_reranked_docs = rerank_documents(retrieval_query, initial_retrieved_docs)
    initial_refined_docs = refine_context(initial_reranked_docs, max_chunks=3)

    initial_evidence = assess_evidence(query, initial_refined_docs)
    initial_confidence = compute_confidence(initial_evidence)
    initial_arbitration = arbitrate_signals(initial_evidence, initial_confidence)
    initial_decision = make_decision(
        initial_evidence,
        initial_confidence,
        initial_arbitration
    )

    verification_result = run_verification_loop(
        query=query,
        vector_store=vector_store,
        chunks=chunks,
        decision=initial_decision,
        max_retries=2
    )

    audit_data = {
        "original_query": rewrite_result.original_query,
        "rewritten_query": rewrite_result.rewritten_query,
        "needs_clarification": rewrite_result.needs_clarification,
        "clarification_reason": rewrite_result.clarification_reason,
        "initial_evidence": initial_evidence,
        "initial_confidence": initial_confidence,
        "initial_arbitration": initial_arbitration,
        "initial_decision": initial_decision,
        "verification_result": verification_result["verification"],
        "final_decision": verification_result["final_decision"],
        "attempts": verification_result["attempts"],
        "final_answer": verification_result["final_answer"],
        "sources": [
            {
                "source": doc.metadata.get("source", "unknown"),
                "content": doc.page_content
            }
            for doc in verification_result["documents"]
        ]
    }

    log_path = write_audit_log(audit_data)
    drift_result = run_drift_detection()

    print("ORIGINAL QUERY:", rewrite_result.original_query)

    print("\nREWRITTEN QUERY:")
    print(rewrite_result.rewritten_query)

    print("\nNEEDS CLARIFICATION:")
    print(rewrite_result.needs_clarification)

    print("\nINITIAL EVIDENCE:")
    print(initial_evidence)

    print("\nINITIAL CONFIDENCE:")
    print(initial_confidence)

    print("\nINITIAL ARBITRATION:")
    print(initial_arbitration)

    print("\nINITIAL DECISION:")
    print(initial_decision)

    print("\nVERIFICATION LOOP RESULT:")
    print(verification_result["verification"])

    print("\nFINAL DECISION:")
    print(verification_result["final_decision"])

    print("\nATTEMPTS:")
    print(verification_result["attempts"])

    print("\nFINAL ANSWER:")
    print(verification_result["final_answer"])

    print("\nAUDIT LOG:")
    print(log_path)

    print("\nDRIFT DETECTION:")
    print(drift_result)


if __name__ == "__main__":
    main()