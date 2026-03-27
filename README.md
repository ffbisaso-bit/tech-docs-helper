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

This is a zero-trust RAG system.

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

## Run locally

1. Create environment

python -m venv .venv  
source .venv/bin/activate  

2. Install dependencies

pip install -U pip  
pip install langchain langchain-openai langchain-community langchain-text-splitters faiss-cpu python-dotenv pydantic  

3. Add environment variables

Create a `.env` file:

OPENAI_API_KEY=your_openai_api_key_here  

4. Run

python src/main.py  

---

## Example behavior

Clear query  
When do health checks run?  
→ Health checks run every 15 seconds.

Operational query  
Why is the service restarting?  
→ The service is restarting because containers failing three health checks restart automatically. Missing environment variables are a common root cause.

Ambiguous query  
When did it start?  
→ ESCALATE (clarification required)

---

## Project structure

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

---

## Tech stack

Python  
LangChain  
OpenAI  
FAISS  
Pydantic  

---

## System capability

- controlled retrieval  
- evidence-based reasoning  
- decision-gated generation  
- verification-driven output  
- observable system behavior via logs and drift signals  