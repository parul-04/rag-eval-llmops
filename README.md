# rag-eval-llmops

A retrieval-augmented generation (RAG) system over the FastAPI documentation, built together with the framework that measures it.

The goal is not just to build a RAG pipeline but to answer: **how do I know whether it is actually good?** Every change (chunk size, top-k, hybrid search) is judged by numbers from a fixed golden dataset, not by eyeballing answers.

> **Status: in progress.** Milestones 0 and 1 (project setup and LLM client) are done. The RAG pipeline and evaluation are being built milestone by milestone; see [Roadmap](#roadmap). Results will appear here only once they have been measured.

---

## Architecture

The project is three pipelines that share code:

```text
A) INDEXING (offline, re-run when chunking changes)

   data/raw/*.md --> ingest --> chunking --> index --> data/index/ (ChromaDB)


B) QUERYING (online, once per question)

   question --> retrieve --> generate --> llm --> Gemini API
                top-k        grounded      retries, token
                chunks       prompt        and latency logging
                                 |
                                 v
                 answer + sources + tokens + latency


C) EVALUATION (runs B over the golden dataset)

   golden questions --> run_eval --> retrieval metrics  (Recall@k, MRR, ...)
                                 --> Ragas metrics      (faithfulness, relevance, ...)
                                 --> results/<run_id>/
```

Design rules:

- **`rag/` never imports from `evaluation/`.** The RAG system does not know it is being tested; the evaluator calls `answer(question)` like any user would.
- **Each external library lives in as few files as possible.** The Gemini SDK is used only in `rag/llm.py`, ChromaDB only in `index.py` and `retrieve.py`. Swapping a provider changes one file.
- **Every result is saved with the config that produced it** (model, embedding model, chunk size, overlap, k, git commit) so any run can be reproduced.

---

## Tech stack

| Component | Choice | Why |
|---|---|---|
| LLM | Google Gemini (`google-genai` SDK) | Free tier; exact model name set in `.env` |
| Embeddings | `BAAI/bge-small-en-v1.5` via `sentence-transformers` | Runs locally, free, deterministic |
| Vector store | ChromaDB | Embedded, persists to disk, supports metadata filters |
| Keyword search | `rank-bm25` | For hybrid retrieval experiments |
| Validation | Pydantic | Structured LLM output and dataset validation |
| Generation metrics | Ragas | Standard LLM-as-judge metrics |
| Tests | pytest | Retrieval metrics must be provably correct |

---

## Project structure

```text
rag-eval-llmops/
├── rag/                      # the RAG system
│   ├── config.py             # settings loaded from .env                  [done]
│   ├── llm.py                # single entry point for LLM calls:
│   │                         # retries with backoff, tokens, latency      [done]
│   ├── ingest.py             # files -> documents                          [planned]
│   ├── chunking.py           # documents -> chunks with overlap            [planned]
│   ├── index.py              # chunks -> embeddings in ChromaDB            [planned]
│   ├── retrieve.py           # question -> top-k chunks                    [planned]
│   └── generate.py           # answer(question): the full RAG system       [planned]
├── evaluation/
│   ├── retrieval_metrics.py  # hit rate, Recall@k, Precision@k, MRR        [planned]
│   ├── ragas_eval.py         # faithfulness, relevance, context metrics    [planned]
│   └── run_eval.py           # runs the golden set, saves results          [planned]
├── scripts/
│   ├── try_llm.py            # temperature and structured output experiments
│   ├── check_models.py       # which models respond right now
│   └── debug_config.py       # isolate request settings when calls fail
├── data/
│   ├── raw/                  # FastAPI tutorial docs (source corpus)
│   └── golden/               # evaluation questions (JSONL)
├── results/                  # evaluation runs
├── tests/
├── .env.example
└── requirements.txt
```

---

## Setup

Tested with Python 3.14 on Windows.

```powershell
git clone https://github.com/parul-04/rag-eval-llmops.git
cd rag-eval-llmops

py -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file from the template and add a Gemini API key from [Google AI Studio](https://aistudio.google.com):

```powershell
Copy-Item .env.example .env
```

```text
GEMINI_API_KEY=your-key-here
LLM_MODEL=gemini-3.1-flash-lite
```

Check which models your key can reach right now, then run the LLM experiments:

```powershell
python -m scripts.check_models
python -m scripts.try_llm
```

All commands run from the project root with `python -m`, so that imports like `from rag.llm import generate` resolve.

---

## Roadmap

| Milestone | Scope | Status |
|---|---|---|
| M0 | Project setup: venv, config, secrets handling | Done |
| M1 | LLM client: token and latency logging, structured output, retry with exponential backoff | Done |
| M1.5 | Context window limits, top-p, `finish_reason` tracking | Planned |
| M2 | Document ingestion and chunking | Planned |
| M3 | Embeddings, ChromaDB index, retrieval | Planned |
| M4 | Grounded generation with citations (baseline RAG) | Planned |
| M5 | Golden dataset: 50 questions with source labels | Planned |
| M6 | Retrieval metrics with unit tests, evaluation runner | Planned |
| M7 | Generation metrics with Ragas | Planned |
| M8 | Experiments: chunk size, top-k, hybrid BM25, reranking | Planned |

Each milestone is tracked as GitHub issues with a task checklist and a "done when" check.

Later additions to the same codebase: input and output guardrails, an observability dashboard, an LLM gateway with routing and fallback, and deployment with FastAPI and Docker.

---

## Findings so far

Observations from Milestone 1 (single runs on the Gemini free tier, so indicative rather than benchmarks):

- **Temperature 0** gave identical answers across runs; temperature 1.0 changed wording only slightly on a factual question.
- **Structured JSON output** cost about 40% more output tokens than plain text for the same answer (49 vs 35).
- **Latency varied more than 5x** (1.3 s to 7.2 s) for identical requests, driven by server load rather than output length. Latency will therefore be reported as average and P95, never as a single number.
- **Model-reported confidence is not a metric.** The model returned `confidence=1.0` for an answer it had no way to verify.
- **Free-tier models regularly return 503** under load, which is why `llm.py` retries with exponential backoff and jitter.

---

## Results

No evaluation results yet. This section will hold the baseline and experiment tables from Milestones 6 to 8, each traceable to a run in `results/`.

---

## Data and license

The documents in `data/raw/` are from the [FastAPI](https://github.com/fastapi/fastapi) project by Sebastián Ramírez, used under the MIT License (see `data/raw/LICENSE-fastapi-docs`).

The code in this repository is released under the [MIT License](LICENSE).