# Tech Docs Helper

A production-grade zero-trust RAG system for technical documentation.

This system does not assume retrieved information is correct.  
Every answer must pass evidence validation and verification before being returned.

---

## What this system does

Tech Docs Helper answers questions from technical documentation using a controlled pipeline.

It does not generate answers directly from retrieval.

Instead, it enforces:

- evidence-based answering
- confidence-driven decisions
- verification before output
- refusal when evidence is insufficient

The system can:

- answer
- refuse
- escalate

based on evidence and validation, not guesswork.

---

## Core principle

This is a **zero-trust RAG system**.

- Retrieval is not trusted  
- Generation is not trusted  
- Only verified, evidence-backed answers are allowed  

If evidence is weak or incomplete, the system refuses.

---

## Architecture

User Query  
→ Query Rewriting  
→ Hybrid Retrieval  
→ Retrieval Reranking  
→ Context Refinement  
→ Evidence Assessment  
→ Confidence Gate  
→ Arbitration  
→ Decision Engine  
→ Generation  
→ Verification Loop  
→ ACT / REFUSE / ESCALATE  
→ Audit Log  
→ Drift Detection

---

## Layer breakdown

### Query Rewriting
Improves the query for retrieval while preserving exact user intent.

Detects ambiguity and triggers escalation when intent cannot be safely inferred.

---

### Hybrid Retrieval
Combines:

- dense retrieval (semantic meaning)
- lexical retrieval (exact term matching)

This improves recall and reduces missed evidence.

---

### Retrieval Reranking
Reorders retrieved documents to surface the most relevant evidence.

---

### Context Refinement
Filters and reduces retrieved content to the strongest, most relevant chunks.

---

### Evidence Assessment
Evaluates whether the retrieved content is sufficient to support answering.

---

### Confidence Gate
Transforms evidence strength into a confidence signal.

---

### Arbitration
Detects conflicting or inconsistent signals.

---

### Decision Engine
Determines whether the system should:

- ANSWER
- REFUSE
- ESCALATE

---

### Generation
Produces an answer only if the decision engine allows it.

---

### Verification Loop
A second model validates:

- the query
- the evidence
- the generated answer

It can:

- PASS the answer
- request RETRY_RETRIEVAL
- request RETRY_GENERATION
- REFUSE
- ESCALATE

---

### ACT / REFUSE / ESCALATE
Final system boundary.

No answer is returned unless it passes all control layers.

---

### Audit Log
Stores full execution traces for every run.

---

### Drift Detection
Monitors system behavior over time to detect degradation in:

- answer rate
- refusal rate
- verification success

---

## Example behavior

### Clear query
Query:  
`When do health checks run?`

Output:  
`Health checks run every 15 seconds.`

---

### Operational query
Query:  
`Why is the service restarting?`

The system retrieves evidence, validates it, and only answers if sufficient support exists.

---

### Ambiguous query
Query:  
`When did it start?`

Output:  
Escalation due to unclear subject.

---

## Project structure

```text
src/
├── main.py
├── config.py
├── loader.py
├── vector_store.py
├── rewrite_query.py
├── hybrid_retrieval.py
├── reranker.py
├── refine_retrieval.py
├── assess_evidence.py
├── confidence_gate.py
├── arbitrate_route.py
├── decision_engine.py
├── generate_answer.py
├── verification_loop.py
├── audit_log.py
├── drift_detection.py

data/
├── api_reference.txt
├── deployment_guide.txt
├── troubleshooting.txt

logs/