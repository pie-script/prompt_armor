# AI Security Gateway — 15-Day Implementation Checklist

> **Tracking in VS Code**:
> - Toggle tasks manually by changing `[ ]` to `[x]`.
> - **Interactive Mode**: Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on macOS) to open the Markdown Preview, where checkboxes can be toggled interactively.
> - **Recommended Extensions**: 
>   - *Markdown All in One* (`yzhang.markdown-all-in-one`): Use `Alt+C` to toggle task completion on the current line.
>   - *Todo Tree* (`Gruntfuggly.todo-tree`): Surface TODO markers across your repository in the activity bar.

---

## Phase 1: Project Scaffolding & The Baseline Proxy (Days 1–3)

- [x] **Day 1: Project Isolation & Environment Setup**
  - [x] Initialize Git repository and create standard directory structure (`models/`, `security/`, `services/`, `dashboard/`, `tests/`)
  - [x] Create and activate Python virtual environment (`python -m venv .venv`)
  - [x] Create `.gitignore` ignoring `.venv/`, `__pycache__/`, `.env`, and test artifacts
  - [x] Install baseline dependencies: `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`

- [x] **Day 2: Configuration & Request Schema Modeling**
  - [x] Implement `config.py` with centralized environment variable loader (host, port, API credentials)
  - [x] Define incoming request schemas in `schemas.py` with string length boundary ($1 \le \text{chars} \le 4000$) and optional `session_id`/`user_id`
  - [x] Define standard clean response schema (status, latency, model payload)
  - [x] Define blocked response schema (`BLOCKED` status, threat classification, triggered security rule)

- [x] **Day 3: Baseline Gateway Routing**
  - [x] Implement `POST /v1/chat` controller in `main.py`
  - [x] Connect input schemas to ensure automated HTTP 422 rejections on schema violations
  - [x] Configure Uvicorn hot-reloading and smoke-test endpoints via Swagger UI at `/docs`

---

## Phase 2: Relational Audit Logging & Persistence (Days 4–6)

- [x] **Day 4: Database Schema Design**
  - [x] Configure SQLite connection and engine in `models/database.py`
  - [x] Define `audit_events` schema with relational columns:
    - [x] `id` (Integer Primary Key, autoincrementing)
    - [x] `timestamp` (DateTime, indexed)
    - [x] `client_ip` (String)
    - [x] `raw_prompt` (Text)
    - [x] `sanitized_prompt` (Text)
    - [x] `decision` (`ALLOWED` or `BLOCKED`)
    - [x] `threat_category` (`NONE`, `LLM01_INJECTION`, `LLM02_LEAK`, `LLM08_CONTEXT_EXTRACTION`)
    - [x] `confidence_score` (Float: $0.0$ to $1.0$)
    - [x] `rule_triggered` (String)

- [x] **Day 5: Database CRUD & Write Operations**
  - [x] Write dedicated event persistence function in `services/audit.py`
  - [x] Implement secure fail-closed error boundaries: if audit writes fail, return standard system errors rather than hanging or leaking state

- [x] **Day 6: Query Endpoints for Security Auditing**
  - [x] Implement read-only endpoint `GET /v1/audit/logs` with pagination (`limit`, `offset`)
  - [x] Add query filter parameter to retrieve only blocked threat entries
  - [x] Verify serialization and pagination behavior via `/docs`

---

## Phase 3: Rule-Based Threat & PII Engines (Days 7–9)

- [x] **Day 7: Heuristic Injection Scanner (Static Detection)**
  - [x] Assemble catalog of jailbreak phrases, role-override directives, and markers in `security/heuristics.py`
  - [x] Implement string normalization helper (whitespace collapse, lowercasing, leetspeak normalization)
  - [x] Implement evaluation logic returning structured verdict (`is_flagged`, `signature`, `severity`)

- [x] **Day 8: Secrets & PII Redaction Engine**
  - [x] Compile regex token patterns for API keys, JWTs, card/ID numbers, emails, and phone numbers in `security/pii_scrubber.py`
  - [x] Implement string transformation replacing sensitive entities with masks (e.g., `[REDACTED_API_KEY]`, `[REDACTED_EMAIL]`)
  - [x] Write unit checks ensuring masked strings (not raw secrets) propagate downstream

- [x] **Day 9: Interceptor Pipeline Integration**
  - [x] Chain heuristic engine and PII scrubber sequentially inside `POST /v1/chat`
  - [x] Test edge case: explicit prompt injections log as `BLOCKED` and return HTTP 403 immediately without external calls
  - [x] Test edge case: PII submissions persist sanitized prompt records and allow request execution to proceed

---

## Phase 4: Autonomous LLM Semantic Judge & Forwarding (Days 10–12)

- [x] **Day 10: Semantic Triage Architecture**
  - [x] Install `google-genai` SDK and configure API keys in `.env`
  - [x] In `security/llm_guard.py`, build AppSec Reviewer judge prompt targeting `gemini-3.5-flash-lite`
  - [x] Enforce machine-readable JSON output: `is_jailbreak` (bool), `risk_category` (str), `risk_score` (float $0.0$–$1.0$), `reasoning` (str)

- [x] **Day 11: Hybrid Evaluation Gating & Downstream Dispatch**
  - [x] Implement decision tree in `services/proxy.py`:
    - [x] Fast heuristic match $\rightarrow$ immediate reject ($0\text{ ms}$ external latency)
    - [x] Clean heuristic $\rightarrow$ conditionally invoke Groq semantic judge on complex prompts
    - [x] High-risk judge verdict $\rightarrow$ record incident to SQLite and return HTTP 403
    - [x] Clean verdict $\rightarrow$ forward prompt to downstream model and capture total latency

- [x] **Day 12: Automated Attack Suite & Adversarial Testing**
  - [x] Build adversarial test runner in `tests/test_attack_suite.py`
  - [x] Create 10 benign enterprise baseline prompts (summarization, SQL queries, code explanations)
  - [x] Create 10 adversarial attacks (jailbreaks, instruction overrides, system-prompt extraction)
  - [x] Execute test suite to confirm $0\%$ false-positive rate on benign queries and $100\%$ interception of adversarial attacks

---

## Phase 5: Visual Dashboard, Packaging & Deliverables (Days 13–15)

- [ ] **Day 13: SOC Analytics Dashboard**
  - [ ] Build Streamlit SOC dashboard in `dashboard/audit_view.py` querying `data/security_logs.db`
  - [ ] Implement key metric indicators:
    - [ ] Total Inspected Prompts
    - [ ] Blocked Attacks (Count & Percentage)
    - [ ] PII Scrub Events
    - [ ] Mean Gateway Latency ($\text{ms}$)
  - [ ] Render live-updating audit log table with severity-badged rows

- [ ] **Day 14: System Hardening & Documentation**
  - [ ] Freeze pinned dependencies to `requirements.txt`
  - [ ] Provide `.env.example` with setup placeholders (`GEMINI_API_KEY`, `GATEWAY_HOST`, `GATEWAY_PORT`)
  - [ ] Write `README.md` following AppSec industry guidelines:
    - [ ] Threat model & OWASP Top 10 for LLM coverage (LLM01, LLM02, LLM08)
    - [ ] Architecture and request pipeline flow diagram
    - [ ] Setup and local launch instructions for FastAPI and Streamlit
    - [ ] Sample `curl` interactions showing HTTP 200 vs HTTP 403 responses

- [ ] **Day 15: Final Verification & Portfolio Artifacts**
  - [ ] Perform fresh end-to-end run: database init, FastAPI boot, Streamlit launch, and payload execution
  - [ ] Capture CLI output screenshot showcasing intercepted HTTP 403 injection attempts
  - [ ] Capture Streamlit dashboard screenshot displaying SOC audit analytics
  - [ ] Commit all code, push clean repository to GitHub, and create release tag