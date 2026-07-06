# CV Screener & Shortlisting Agent

An AI-powered recruitment assistant that automatically screens CVs against a job description, scores each candidate, generates a shortlist, and produces a final recruitment report — with a human-in-the-loop review step before the report is finalized.

---

## How It Works

A recruiter submits a job description and a set of CV files. The agent extracts the key requirements from the job description, scores each CV in parallel, filters and ranks candidates into a shortlist, then pauses and waits for the recruiter to review and approve before generating the final report.

```
Job Description + CVs
        ↓
[requirements_extractor] → extracts must-have and nice-to-have skills
        ↓
[scorer × N] → scores each CV in parallel using the Send API
        ↓
[shortlister] → filters scores ≥ 0.7, ranks by score
        ↓
[human_in_the_loop] → pauses, recruiter reviews and approves
        ↓
[report_generator] → generates final recruitment report
        ↓
Final Report
```

---

## Features

- **Automatic requirement extraction** — parses must-have and nice-to-have skills from any job description
- **Parallel CV scoring** — all CVs are scored simultaneously using LangGraph's Send API
- **Structured scoring** — each candidate gets a score (0–1) with a written justification
- **Smart shortlisting** — only candidates scoring ≥ 0.7 are shortlisted, ranked by score
- **Human-in-the-loop** — recruiter approves or rejects the shortlist before the report is generated
- **Final report generation** — professional recruitment report summarizing shortlisted candidates
- **State persistence** — full session state saved between API calls via checkpointer

---

## Project Structure

```
cv_screener/
│
├── main.py                        # FastAPI app + all code (monolithic, pre-split)
│
├── api/
│   ├── schemas.py                 # Request/response Pydantic models
│   └── routers/
│       ├── screen.py              # POST /screen
│       ├── confirm.py             # POST /confirm
│       └── report.py              # GET /report
│
├── graph/
│   ├── state.py                   # State + CVScorerState TypedDicts
│   ├── builder.py                 # Node registration + edge wiring
│   └── instance.py                # Compiled graph instance
│
├── nodes/
│   ├── requirements_extractor.py  # Extracts job requirements
│   ├── cv_scorer.py               # Scores one CV against requirements
│   ├── shortlister.py             # Filters and ranks candidates
│   ├── human_in_the_loop.py       # Pauses for recruiter review
│   └── report_generator.py        # Generates final report
│
└── config/
    └── llm.py                     # ChatGroq LLM instance
```

---

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — agent graph orchestration, Send API for parallel scoring, human-in-the-loop
- **[LangChain](https://github.com/langchain-ai/langchain)** — LLM abstraction and structured output
- **[Groq](https://groq.com/)** — LLM inference (`llama-3.3-70b-versatile`)
- **[FastAPI](https://fastapi.tiangolo.com/)** — REST API layer
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — PDF text extraction
- **[Pydantic](https://docs.pydantic.dev/)** — data validation for LLM output and API schemas

---

## Installation

```bash
git clone https://github.com/your-username/cv-screener
cd cv-screener
pip install -r requirements.txt
```

Create a `.env` file at the root:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the API

```bash
uvicorn main:app --reload
```

API available at `http://127.0.0.1:8000`
Interactive docs at `http://127.0.0.1:8000/docs`

---

## API Endpoints

### `POST /screen`
Submit a job description and CV filenames to start the screening process.

**Request (multipart form):**
```
job_description: "We are looking for an AI Engineer..."
thread_id: "recruitment-001"
cv_filenames: "cv1.pdf"
cv_filenames: "cv2.pdf"
```

**Response (interrupted — awaiting recruiter review):**
```json
{
  "scores": [
    {
      "filename": "cv1.pdf",
      "score": 0.9,
      "justification": "Strong match on all must-have requirements..."
    },
    {
      "filename": "cv2.pdf",
      "score": 0.3,
      "justification": "Background in marketing, lacks technical skills..."
    }
  ],
  "shortlist": [
    {
      "filename": "cv1.pdf",
      "score": 0.9,
      "justification": "Strong match on all must-have requirements..."
    }
  ],
  "interrupted": true,
  "interrupt_question": "Please review the shortlist. Do you approve it? (approve / adjust / reject)"
}
```

---

### `POST /confirm`
Resume the graph after recruiter reviews the shortlist.

**Request:**
```json
{
  "decision": "approve",
  "thread_id": "recruitment-001"
}
```

**Decisions:**
| Value | Meaning |
|---|---|
| `approve` | Accept the shortlist, generate the final report |
| `reject` | Discard the shortlist, no report generated |

**Response:**
```json
{
  "final_report": "## Recruitment Report\n\nAfter screening 2 candidates against the AI Engineer role...\n\n**Shortlisted Candidates:**\n\n- cv1.pdf (Score: 0.90)..."
}
```

---

### `GET /report`
Retrieve the final report for a completed screening session.

**Request:**
```
GET /report?thread_id=recruitment-001
```

**Response:**
```json
{
  "final_report": "## Recruitment Report\n\n..."
}
```

---

### `GET /health`
Check that the server is running.

```json
{ "status": "ok" }
```

---

## State Schema

The graph carries this state across all nodes:

| Field | Type | Description |
|---|---|---|
| `job_description` | `str` | Raw job description text |
| `cvs` | `list[dict]` | List of `{filename, text}` dicts |
| `requirements` | `dict` | Extracted `{must_have, nice_to_have}` lists |
| `scores` | `Annotated[list, add]` | Accumulated scores from parallel CV scoring |
| `shortlist` | `list[dict]` | Filtered and ranked candidates |
| `reviewed` | `bool` | Whether recruiter has approved the shortlist |
| `final_report` | `str` | Generated recruitment report |

---

## The Send API — Parallel CV Scoring

Each CV is scored independently and in parallel using LangGraph's Send API:

```python
def distribute_cvs(state: State):
    return [
        Send('scorer', {'cv': cv, 'requirements': state['requirements']})
        for cv in state['cvs']
    ]
```

Each `Send` call creates an isolated mini-state for one CV and runs `score_cv` in parallel. Results accumulate back into `state['scores']` via the `add` reducer. This means 10 CVs are scored simultaneously, not sequentially.

---

## Example Session

```
1. Recruiter submits job description + 3 CV files
        ↓
2. Agent extracts: must_have = [Python, FastAPI, LangChain, ...]
        ↓
3. Agent scores all 3 CVs in parallel:
   - cv1.pdf: 0.92 — strong technical match
   - cv2.pdf: 0.74 — good match, missing Docker experience  
   - cv3.pdf: 0.21 — marketing background, not relevant
        ↓
4. Shortlist generated: [cv1.pdf, cv2.pdf] (scores ≥ 0.7)
        ↓
5. API returns interrupted=true, shows shortlist to recruiter
        ↓
6. Recruiter sends decision: "approve"
        ↓
7. Agent generates final recruitment report
        ↓
8. Recruiter retrieves report via GET /report
```

---

## Notes

- CV files must be placed in the same directory as `main.py` when using filename-based input
- `thread_id` must be generated and managed by the client to maintain session state across `/screen` and `/confirm` calls
- The graph uses `InMemorySaver` as checkpointer — state is lost on server restart. For production, replace with a persistent checkpointer (PostgreSQL, Redis)
- The shortlist threshold is currently hardcoded at `0.7` in `shortlist_cvs` — this can be made configurable via the request schema
