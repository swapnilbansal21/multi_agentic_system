# SMMS-Agent — Complete Project Document (v1)

**Author:** Swapnil Bansal
**Base project:** SMMS (Smart Meeting Management System) — originally built for Chandigarh Administration in React Native / Expo, Clean Architecture.
**This doc covers:** Evolving SMMS into a production multi-agent GenAI product — full requirements, tech stack, architecture, deployment, security, testing, build plan.
**Status:** Draft v1 for review before code starts
**Target build window:** 6 weeks solo (Sep 15 – Oct 25, 2026)

---

## 1. Context — where SMMS is today, where SMMS-Agent goes

**Today (SMMS v1 — already built):**
- React Native / Expo mobile app
- Clean Architecture (data / domain / presentation layers)
- Delivered for Chandigarh Administration users (govt officials, department heads, PAs)
- Core features: create meeting, invite attendees, set agenda, view calendar, attach files, capture minutes manually

**Tomorrow (SMMS-Agent v2 — this project):**
Same domain, same app foundation, but now **7 AI agents** work autonomously behind the UI to handle everything a good executive assistant does:
- Schedule meetings across many officials' calendars
- Compose draft agendas from past meeting context
- Send pre-meeting briefs personalized per attendee
- Transcribe meetings live (Hindi + English)
- Extract decisions + action items + owners from transcripts
- Auto-generate follow-up emails and task-tracker entries
- Surface cross-meeting insights (blocked action items, recurring topics)

> **Hinglish — kyun evolution, fresh nahi:** Foundation already deployed hai — screens, navigation, DB models, auth ready. Zero se banane mein 3 hafte foundation pe lagte. Yahaan agentic layer pe direct focus — 6 hafte ka time actually agent quality pe milega. Aur resume-story alag hi level ki hai: *"Delivered a meeting-management system for Chandigarh Administration, then evolved it into a multi-agent GenAI product on Azure with 4 custom MCP servers."*

---

## 2. Problem statement

Government officials, department heads, and executives spend 40–60% of their working week in meetings. Around each meeting there's invisible work — scheduling coordination, agenda drafts, pre-meeting reading, minute-taking, action-item chasing. Today this work either falls on personal assistants (expensive, limited to VIPs) or falls through the cracks (most common — action items never followed up, decisions forgotten, same topics re-discussed).

SMMS v1 solved the surface — a mobile app for managing meetings. SMMS-Agent v2 solves the invisible work — an autonomous AI executive assistant embedded in the same app.

### Real pain today (Chandigarh Admin officials, verified during SMMS v1 field usage)

- Department heads have 8–12 meetings/day; agenda often composed 5 minutes before joining
- Minutes recorded on paper or Whatsapp, transcribed manually later (or not at all)
- Action items assigned verbally, forgotten by next meeting
- Scheduling requires 4–5 back-and-forth emails per meeting
- Hindi + English mix common — English-only transcription tools fail

### Success — what "solved" looks like

- Meeting scheduled with 1 click across all attendees' Outlook/Google calendars
- Draft agenda auto-generated from past meetings on same topic
- Personalized pre-meeting brief in each attendee's inbox 1 hour before
- Live bilingual transcription visible in the meeting screen
- Auto-extracted action items appear in each owner's task list within 30 seconds of meeting end
- Follow-up mail drafts ready to send to attendees

---

## 3. Users (personas)

### Persona 1: Anita — Additional Secretary, Chandigarh Administration
- 15 years service, 6–8 meetings daily
- Reports to Chief Secretary + manages 4 department heads
- Pain: no time to prep, misses action items assigned to her in cross-department meetings
- Wants: brief before each meeting, action-item digest end of day

### Persona 2: Rajesh — PA to Deputy Commissioner
- Coordinates DC's calendar with 40+ officials
- Pain: schedules 20 meetings/day, spends 60% of time on back-and-forth
- Wants: agent that finds slots + drafts invites in Hindi + English

### Persona 3: Meera — Junior Officer (attendee, not organizer)
- Attends 3–5 meetings weekly
- Pain: assigned action items in meetings but forgets, gets escalations
- Wants: her personal action-item list auto-populated from meeting transcripts

**Primary persona for v1:** Rajesh (PA) — highest volume, most demonstrable ROI.

---

## 4. Detailed use case scenarios

### Scenario A: Rajesh schedules an inter-department review

**Today:**
- Emails 6 department heads asking for availability next week
- 3 reply within 2 days, 3 don't reply
- Follow-up on Whatsapp
- Finally settles on Wednesday 3 PM
- Manually types agenda from prior meeting notes he finds in email
- Sends calendar invites individually
- Total effort: ~2 hours over 4 days

**With SMMS-Agent:**
- Opens app, taps "New meeting"
- Adds 6 attendees, meeting topic, priority "high"
- **Scheduler Agent** reads all 6 calendars via MCP-calendar, finds Wednesday 3 PM slot open for 5, Thursday 4 PM open for all 6
- Rajesh confirms Thursday 4 PM
- **Agenda Composer Agent** searches past meetings tagged with related topics (RAG over meeting archive), drafts a 5-point agenda in Rajesh's writing style
- Rajesh edits, taps "Send"
- Calendar invites auto-sent, agenda attached, in Hindi + English
- **Total effort: 4 minutes**

### Scenario B: During the meeting

- Live transcription runs on-device (privacy) via Azure Speech + custom Hindi model
- Screen shows real-time transcript, speaker labels, and a rolling summary in a side panel
- Meera notices agent flagged "Meera to submit RTI compliance report" as an action item assigned to her, with due date auto-inferred

### Scenario C: After the meeting

- Within 60 seconds of meeting end, **Action Extractor Agent** identifies 8 action items, 3 decisions, 2 open questions
- **Follow-Up Agent** generates:
  - Draft email to attendees with minutes summary
  - Task-tracker entries for each action item (owner + due date)
  - Calendar events for follow-up meetings mentioned in the discussion
- All in Hindi + English side-by-side
- Rajesh reviews once, taps "Send all"

### Scenario D: Weekly cross-meeting insight

- Every Friday, **Insight Agent** sends Rajesh a digest:
  - "3 action items assigned to Officer X are pending > 2 weeks"
  - "Topic 'Smart City phase 2' has come up in 5 meetings this week — consider consolidating"
  - "Meeting XYZ was scheduled and cancelled 3 times — may need decision on necessity"

---

## 5. Functional requirements

### 5.1 Meeting scheduling
- **FR-01 (MUST):** User can select multiple attendees; system reads their calendars via MCP-calendar and returns top-3 slot suggestions.
- **FR-02 (MUST):** System supports both Google Calendar and Microsoft Outlook (via MS Graph).
- **FR-03 (MUST):** Slot suggestions respect working hours + declared holidays + India public holidays.
- **FR-04 (SHOULD):** User can lock a slot; system sends invites in bulk.

### 5.2 Agenda composition
- **FR-05 (MUST):** Agenda Composer Agent uses RAG over past meeting minutes to draft an agenda relevant to the topic.
- **FR-06 (MUST):** Agenda output is bilingual (Hindi + English side by side).
- **FR-07 (SHOULD):** User can accept, edit, or regenerate the draft.

### 5.3 Pre-meeting brief
- **FR-08 (MUST):** 1 hour before every meeting, Prep Brief Agent generates a per-attendee brief containing: their pending action items from prior meetings + relevant background docs + summary of last meeting on this topic.
- **FR-09 (SHOULD):** Brief delivered via in-app notification + email.

### 5.4 Live transcription
- **FR-10 (MUST):** Live transcription during the meeting with speaker diarization.
- **FR-11 (MUST):** Bilingual — Hindi + English mixed sentences correctly transcribed.
- **FR-12 (SHOULD):** Rolling summary updates every 60 seconds during the meeting.
- **FR-13 (SHOULD):** User can flag any transcript segment as "important" for later review.

### 5.5 Action extraction
- **FR-14 (MUST):** Within 60 seconds of meeting end, Action Extractor Agent produces a list of action items with (task, owner, due date, source_transcript_span).
- **FR-15 (MUST):** Confidence score attached to each item; low-confidence items flagged for user review.
- **FR-16 (MUST):** Decisions and open questions extracted separately.

### 5.6 Follow-up automation
- **FR-17 (MUST):** Follow-Up Agent drafts a summary email in Hindi + English.
- **FR-18 (MUST):** Task-tracker entries auto-created (Jira / Asana / Trello / native SMMS tasks).
- **FR-19 (MUST):** User approves before any email is sent or task is created — no autonomous side effects.

### 5.7 Cross-meeting insights
- **FR-20 (SHOULD):** Weekly digest identifies overdue action items, recurring topics, cancelled-repeatedly meetings, and outstanding decisions.

### 5.8 Language + audit
- **FR-21 (MUST):** UI supports English + Hindi toggle; all agent-generated text bilingual.
- **FR-22 (MUST):** Full audit log — every agent action, every LLM call, every user approval — persisted for 1 year (government compliance).

---

## 6. Non-functional requirements

- **NFR-01:** Live transcription latency ≤ 3 seconds behind live audio p95.
- **NFR-02:** Action extraction produces first draft ≤ 60 seconds after meeting ends.
- **NFR-03:** Meeting scheduling suggestion returns in ≤ 5 seconds even with 10 attendees.
- **NFR-04:** Availability 99.5% during working hours (09:00–19:00 IST).
- **NFR-05:** Data residency — all data stored in India regions only (DPDP Act 2023).
- **NFR-06:** All meeting transcripts encrypted at rest (AES-256) + in transit (TLS 1.2+).
- **NFR-07:** PII (Aadhaar, PAN, phone) auto-redacted from transcripts before LLM exposure.
- **NFR-08:** LLM cost per meeting p95 ≤ ₹8.
- **NFR-09:** All agent decisions traceable in Langfuse for audit.

---

## 7. Budget

### 7.1 Build cost — solo, 6 weeks
Your time: ~144 hours over 6 weeks (evenings + weekends).

### 7.2 Tooling / subscriptions
| Item | ₹ |
|---|---|
| GitHub (public repo) | 0 |
| Domain (optional) | 800/yr |
| Expo EAS build (existing app) | 0 (free tier) |
| **Build-side tooling ceiling** | ₹1,500 total |

### 7.3 Azure run cost (approximate, Central India)
| Service | Purpose | ₹/month |
|---|---|---|
| Container Apps (API + 4 MCP servers + Langfuse) | Compute | 1,500–3,500 |
| Postgres Flexible Server B1ms | App + RAG + audit | 900 |
| Azure OpenAI (GPT-4o + GPT-4o-mini + Whisper API) | LLM + transcription | 500–2,500 |
| Azure Speech Services (Hindi model) | Live transcription | 400–1,200 |
| Static Web App | React Native web build (optional) | 0 (free tier) |
| ACR + Key Vault + Log Analytics + Blob | Support | 700 |
| **Total dev-phase** | | **4,000–8,800** |

### 7.4 Ceiling
- Build-side tooling: ₹1,500
- Azure dev (Sep 15 – Oct 25): ₹6,000 total
- Azure demo (post-launch, per month): ₹4,000
- Hard kill switch: > ₹500/day = scale all services to zero

---

## 8. Tech stack (locked)

### 8.1 Frontend
- **React Native / Expo** — existing SMMS foundation, keep it
- **TypeScript** — for new agent-related screens
- **@shopify/flash-list** — meeting list virtualization
- **Zustand + TanStack Query** — state + server cache
- **@microsoft/fetch-event-source** — SSE streaming for live transcription
- **MSAL Native SDK** — Entra ID auth (govt SSO)
- **Reanimated** — smooth agent-status animations

### 8.2 Backend
- **FastAPI** (Python 3.12)
- **Pydantic v2** — validation + LLM structured output
- **SQLAlchemy async + asyncpg** — Postgres
- **Alembic** — migrations
- **LangGraph 0.4+** — agent orchestration
- **MCP Python SDK** — build custom MCP servers
- **Instructor + OpenAI SDK** — LLM calls

### 8.3 AI / LLM
- **Azure OpenAI**
  - GPT-4o — Planner, Agenda Composer, Action Extractor (reasoning)
  - GPT-4o-mini — Prep Brief, Follow-Up Writer (volume)
  - text-embedding-3-small — RAG embeddings
- **Azure Speech Services**
  - Custom Hindi model + English speech-to-text
  - Speaker diarization
- **bge-reranker-v2-m3** (local ONNX) — cross-encoder rerank
- **pgvector 0.7+** on Azure Postgres — vector store

### 8.4 MCP servers (custom-built, 4 total)
- **mcp-calendar** — Google Calendar + MS Graph unified interface (find slots, create events, list events)
- **mcp-transcription** — Azure Speech wrapper (start stream, get final transcript, diarize)
- **mcp-email** — Gmail + Outlook via Graph (draft, send with approval, thread)
- **mcp-tasks** — Jira + Asana + native SMMS tasks (create, update, list per owner)

### 8.5 Azure
- Container Apps (API + 4 MCP + Langfuse)
- Static Web App (React Native web export, optional)
- Postgres Flexible Server + pgvector
- Blob Storage (audio files, attachments)
- Key Vault + Managed Identity
- Application Insights + Log Analytics
- Bicep IaC

### 8.6 CI/CD
- GitHub Actions with OIDC to Azure
- 6 workflows: ci, cd-dev, cd-staging, cd-prod, security-scan, expo-mobile-build

### 8.7 Testing / evals
- pytest + testcontainers
- Playwright (web) + Detox (native)
- promptfoo — prompt regression
- Ragas — RAG quality
- Custom eval: 30 sample meeting transcripts → expected action items (recall ≥ 90%)

### 8.8 Observability
- Langfuse self-hosted (LLM traces + cost)
- OpenTelemetry → Application Insights (infra spans)
- Log Analytics (structured JSON logs)

---

## 9. Architecture — 7 agents + supervisor

```
                        User (Rajesh in mobile app)
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │       FastAPI backend          │
                    │  ┌──────────────────────────┐  │
                    │  │  LangGraph SUPERVISOR    │  │
                    │  └────────────┬─────────────┘  │
                    └───────────────│────────────────┘
                                    │
        ┌─────────────┬─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │Scheduler│  │  Agenda  │  │   Prep   │  │Note-Taker│  │  Action  │
   │  Agent  │  │ Composer │  │  Brief   │  │  Agent   │  │Extractor │
   └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
        │            │             │             │             │
        └────────────┴──────┬──────┴─────────────┴─────────────┘
                            ▼
                ┌───────────────────────┐
                │      Follow-Up        │
                │        Agent          │
                └───────────┬───────────┘
                            ▼
                ┌───────────────────────┐
                │       Insight         │
                │        Agent          │
                └───────────┬───────────┘
                            │
       ┌────────────────────┴────────────────────┐
       ▼                                          ▼
┌──────────────┐                          ┌────────────────┐
│ MCP servers  │                          │ Azure Postgres │
│  calendar    │                          │ + pgvector RAG │
│  transcription│                         │ (past minutes) │
│  email       │                          └────────────────┘
│  tasks       │
└──────────────┘
```

### 9.1 Agent contracts

| Agent | Input | Output | Model |
|---|---|---|---|
| **Scheduler** | attendees[], duration, priority | 3 slot suggestions with confidence | GPT-4o |
| **Agenda Composer** | topic, attendees, past_meeting_ids | Bilingual 5-point agenda draft | GPT-4o |
| **Prep Brief** | attendee_id, meeting_id | Per-attendee brief (pending items + docs + context) | GPT-4o-mini |
| **Note-Taker** | audio_stream | Transcript segments + speaker + rolling summary | Azure Speech + GPT-4o-mini |
| **Action Extractor** | full_transcript | Action items[], decisions[], open questions[] | GPT-4o |
| **Follow-Up** | action_items, decisions | Email draft + task entries | GPT-4o-mini |
| **Insight** | last_7_days_meetings | Weekly digest of overdue/recurring/blocked | GPT-4o |

---

## 10. RAG architecture

Same 3-corpus pattern as DataParity, adapted:

| Corpus | Content | Chunking | Retrieved by |
|---|---|---|---|
| **Past-Meetings Archive** | All prior meeting minutes with metadata (topic, attendees, date, dept) | One chunk per agenda item, ~300 tokens | Agenda Composer, Prep Brief, Insight |
| **Action-Items Ledger** | Every action item with status, owner, meeting_id | One row per item | Insight, Prep Brief |
| **Org Directory** | Officer directory, roles, reporting lines, departments | One card per officer | Scheduler (for slot preference), Follow-Up (email routing) |

**Retrieval pipeline:** query rewriter → hybrid (pgvector HNSW + BM25 via `pg_trgm`) → RRF fusion k=60 → cross-encoder rerank → top-5.

**Multilingual note:** Hindi queries embedded with `text-embedding-3-small` (multilingual support built-in — Azure OpenAI). Or fallback to local `LaBSE` model for stronger Hindi.

---

## 11. Data model (Postgres) — new tables on top of existing SMMS schema

```
meetings (existing — extended)
├── + language_pref TEXT ('hi', 'en', 'both')
├── + agent_run_id UUID (FK)
└── + transcript_status TEXT

agent_runs (new)
├── id, meeting_id, agent_name, status, cost_paise, hop_count, started_at, completed_at

transcripts (new)
├── id, meeting_id, segment_order, speaker_id, text_en, text_hi, timestamp_ms, is_flagged

action_items (extended)
├── + extracted_by TEXT ('user' | 'agent')
├── + confidence FLOAT
├── + source_transcript_span JSONB

rag_chunks (new)
├── id, corpus, content, embedding VECTOR(1536), metadata JSONB, tsv TSVECTOR

audit_log (new — appendonly)
├── id, actor, action, resource_type, resource_id, payload_hash, created_at
```

---

## 12. Azure deployment topology

```
Resource Group (rg-smms-agent-<env>)
├── VNet with private subnets
├── Managed Identity (uami-smms-<env>)
├── Container Apps Environment
│   ├── App: api (FastAPI)
│   ├── App: mcp-calendar (internal)
│   ├── App: mcp-transcription (internal)
│   ├── App: mcp-email (internal)
│   ├── App: mcp-tasks (internal)
│   └── App: langfuse (internal)
├── Static Web App (optional web version of the app)
├── Postgres Flexible Server + pgvector
├── Azure OpenAI (GPT-4o + mini + embeddings)
├── Azure Speech Services (Hindi + English models)
├── Blob Storage (audio, attachments)
├── Key Vault
├── ACR
├── Log Analytics + App Insights
└── Front Door + WAF (prod only)
```

Mobile app itself distributed via Expo EAS build → Google Play + Apple App Store (or side-loaded APK for govt-issued devices).

---

## 13. Security & compliance (extra strict — govt data)

- **Data residency:** all data in Azure Central India + South India (DR)
- **DPDP Act 2023 compliance:** consent capture + data-subject rights (delete/export) endpoints
- **Encryption:** AES-256 rest, TLS 1.2+ transit, TDE on Postgres
- **PII redaction:** Aadhaar / PAN / phone auto-detected in transcripts before LLM exposure
- **Audit log retention:** 1 year hot, 5 years cold (Blob archive)
- **Authentication:** Entra ID + optional Aadhaar-linked SSO for Chandigarh Admin (via SecureLink)
- **RBAC:** Officer / PA / Admin roles; strict least-privilege
- **Meeting recording consent:** audio recording requires explicit in-app consent from all attendees before transcription starts
- **10 CI security-scan layers:** gitleaks, ruff-security, bandit, semgrep, pip-audit, checkov, trivy, OWASP ZAP baseline, pnpm audit, license scan
- **LLM security:** prompt injection classifier, hop cap, cost cap, per-user rate limit

---

## 14. Testing strategy — 11 layers (from DataParity playbook, adapted)

Same pyramid. New golden datasets:
- **Meeting transcript benchmark** — 30 sample bilingual transcripts with expected (action items, decisions, questions)
- **Scheduling benchmark** — 20 attendee-calendar setups, expected slot suggestions
- **Hindi transcription accuracy** — 50 audio clips, expected transcript (WER ≤ 20% target)

CI thresholds:
- Action extraction recall ≥ 90%
- Scheduling suggestion precision ≥ 85% (top-3 slot actually free)
- Ragas faithfulness ≥ 0.80 on agenda drafts
- Zero PII leaked to LLM (integration test)

---

## 15. Observability & SLOs

- Live transcription latency p95 ≤ 3s
- Action extraction end-to-end ≤ 60s
- Scheduling suggestion ≤ 5s
- Availability 99.5% (working hours)
- Cost/meeting p95 ≤ ₹8
- Traces: Langfuse (LLM) + App Insights (infra)

---

## 16. 6-week build plan

### Week 1 (Sep 15–21) — Foundation
- Fork existing SMMS repo → new agent branch
- Bicep landing zone deployed (RG, VNet, Key Vault, Log Analytics)
- Postgres + pgvector deployed
- FastAPI skeleton with `/healthz`
- GitHub Actions with OIDC to Azure
- **Tag `v2.0.0-alpha1`**

### Week 2 (Sep 22–28) — Scheduler + Calendar MCP
- `mcp-calendar` server (Google + MS Graph)
- LangGraph supervisor + Scheduler agent
- API endpoint `/schedule-meeting`
- React Native screen: "New Meeting → AI Suggested Slots"

### Week 3 (Sep 29 – Oct 5) — Agenda + RAG
- Seed past-meetings archive from existing SMMS DB
- pgvector setup + hybrid retrieval + reranker
- Agenda Composer agent
- Bilingual Hindi + English output

### Week 4 (Oct 6–12) — Transcription + Note-Taker
- `mcp-transcription` server (Azure Speech)
- Live streaming from mobile → backend → Speech → transcript
- Note-Taker agent for rolling summaries
- React Native meeting screen with live transcript view

### Week 5 (Oct 13–19) — Action Extractor + Follow-Up
- Action Extractor agent
- `mcp-email` + `mcp-tasks` servers
- Follow-Up agent generates email drafts + task entries
- Human approval flow

### Week 6 (Oct 20–25) — Insight + Polish + Demo
- Insight agent (weekly digest)
- Load test with 50 concurrent meetings
- Full eval sweep — CI thresholds must all pass
- Demo Loom video, blog post, LinkedIn announcement
- **Tag `v2.0.0`**

### Buffer (Oct 26–31)
- Bug fixes, resume update with real numbers, interview prep

---

## 17. Day 1 concrete (Monday Sep 15)

**Hour 1:** Clone existing SMMS repo, create `agent-layer` branch, add monorepo structure for `apps/api/` (FastAPI) + keep existing `apps/mobile/` (React Native).
**Hour 2:** Bicep `main.bicep` + landing zone modules — deploy.
**Hour 3:** Postgres Flexible Server + pgvector — deploy, migrate existing SMMS schema.
**Hour 4:** FastAPI skeleton with `/healthz` + Dockerfile — local run.
**Hour 5:** ACR + first image push.
**Hour 6:** Container Apps `api` — deploy, verify live URL.
**Hour 7:** GitHub Actions `ci.yml` + `cd-dev.yml` with OIDC federation.
**Hour 8:** First LLM call from FastAPI hitting Azure OpenAI — `/debug/echo-llm` returns real GPT-4o response.

**End of Day 1:** foundation deployed, CI green, LLM call working, 8 clean commits.

---

## 18. Success metrics

**Product:**
- Action extraction recall ≥ 90% on benchmark
- Hindi transcription WER ≤ 20%
- Scheduling suggestion accuracy ≥ 85%
- Cost per meeting p95 ≤ ₹8
- Zero PII leaked to LLM (verified)

**Career:**
- Live demo URL
- 4 public MCP-server repos
- Blog post + Loom demo + LinkedIn
- Resume updated: *"Extended SMMS (deployed for Chandigarh Administration) into a production multi-agent GenAI system on Azure — 7 agents, 4 custom MCP servers, bilingual Hindi+English support, DPDP-compliant."*

---

## 19. Open questions — Swapnil to answer

1. Is SMMS v1 still deployed for Chandigarh Administration? (Deployed = resume gold; discontinued = still fine as foundation.)
2. Existing SMMS backend — Node/Firebase/other? (Do we replace with FastAPI or extend?)
3. Existing SMMS repo — private or public GitHub? (Public from day 1 recommended.)
4. Azure OpenAI access — approved yet?
5. Chandigarh Administration data — do we have permission to use redacted sample transcripts as demo, or use synthetic data only?
6. Hindi transcription — is Azure Speech Hindi model good enough or need custom fine-tune?

---

## 20. How to use this doc with Claude Code

Yeh section specifically tere workflow ke liye — kyunki tu Claude Code use kar raha hai coding mein.

### Step 1 — Doc ko repo ke andar rakh

Repo bootstrap ke baad, doc ko yahaan save kar:
- `docs/PROJECT_SPEC.md` (this document)
- Ek chhota `CLAUDE.md` repo root pe jo Claude Code ko high-level context deta hai

### Step 2 — CLAUDE.md ka structure

Root level pe `CLAUDE.md` file mein likh:

```
# CLAUDE.md — Instructions for Claude Code

## Project
SMMS-Agent — multi-agent GenAI extension of Chandigarh Admin's meeting management system.
Full spec: @docs/PROJECT_SPEC.md

## Code conventions
- Python 3.12, Ruff + Mypy strict
- FastAPI async everywhere, Pydantic v2 models
- SQLAlchemy 2.0 async style — no sync sessions
- React Native TypeScript, Zustand for state, Tailwind (nativewind)
- Every new endpoint: add unit test + integration test
- Every prompt: version it in src/prompts/ and add promptfoo case

## Never do
- Generate synchronous DB code
- Introduce a new dependency without asking
- Skip eval gate in CI
- Add write tools to any MCP server (must stay read-only)

## Ask before
- Adding new npm/pip dependencies
- Changing schema (Alembic migration required)
- Editing any file under infra/ (Bicep infra changes)

## Reference files
- Architecture: @docs/PROJECT_SPEC.md#9-architecture
- FR list: @docs/PROJECT_SPEC.md#5-functional-requirements
- Testing: @docs/PROJECT_SPEC.md#14-testing-strategy
```

### Step 3 — Claude Code ke andar file reference kaise karte hain

Claude Code CLI shell mein `@` syntax works:
- `@docs/PROJECT_SPEC.md` — entire spec load karta hai context mein
- `@docs/PROJECT_SPEC.md#5-functional-requirements` — specific section
- `@apps/api/src/agents/scheduler.py` — specific file

**Example prompt tu de sakta hai Claude Code ko:**

> *"Read @docs/PROJECT_SPEC.md#5-1-meeting-scheduling and implement FR-01 as a FastAPI endpoint at `apps/api/src/routers/scheduling.py`. Follow the code conventions in @CLAUDE.md. Add unit tests. Do not create new dependencies."*

Claude Code doc padhega, existing conventions samjhega, code likhega, tests likhega. Tu review karega, merge karega.

### Step 4 — Iterative workflow (feature-by-feature)

Har feature ka ek prompt pattern:
1. **Read** — "Read @docs/PROJECT_SPEC.md#<section>"
2. **Understand** — "Explain what FR-XX asks in your own words"
3. **Plan** — "Outline the files you'll touch"
4. **Confirm** — user tu bolega "go"
5. **Implement** — Claude Code writes
6. **Test** — Claude Code runs tests
7. **Commit** — Claude Code drafts commit message

Yeh 7-step loop repeat kar har FR ke liye. Tu 6 hafte mein ~25 features implement kar sakta hai is loop se.

### Step 5 — Claude Code specific tricks

- **Slash commands** — `/init` for setting up project rules; `/plan` for larger changes to review before code
- **`/compact`** — jab context bhar jaaye, use kar
- **`.claude/` folder** — repo-scoped subagents rakh sakta hai (e.g. reviewer, tester, doc-writer)
- **Hooks** — pre-commit se ruff + mypy auto-run, Claude Code se pehle
- **`.gitignore`** — `.claude/state/` gitignore mein daal (per-user state)

### Step 6 — Ek chhoti practical baat

Doc **long** hai (~800 lines). Claude Code isse ek shot mein context mein le sakta hai (200k+ tokens), lekin efficient rehta hai agar tu specific sections reference karta hai. Full doc har turn mein load karne se cost aur latency dono badhte hain.

**Pattern:** pehle turn mein full doc load — "please read and confirm you understand". Aage har feature ke turn mein sirf relevant section reference kar.

---

## 21. Bottom line

Yeh doc SMMS-Agent ka **complete requirements + build spec + Day-1 plan + Claude Code workflow** — sab ek jagah.

**Aage kya:**
1. §19 ke 6 open questions ka jawab de (SMMS current status, backend, repo, Azure OpenAI, data permissions, Hindi transcription)
2. Agar sab clear hai toh **"lock"** bol
3. Kal Monday Sep 15 subah 9 baje Hour 1 se code start
