# 💼 CareerPlus

### Agentic Company Intelligence & Spontaneous Application Platform

CareerPlus is an **Agentic AI + RAG platform for discovering relevant companies and preparing personalized spontaneous applications**.

It combines a structured company database, hybrid retrieval, LLM reasoning, LinkedIn intelligence, project-aware personalization, CV selection, and email automation.

The system runs on a **local Qwen3 8B model** and uses an agent to decide which tools are required for each user request.

> **Company Intelligence → Retrieval → Reasoning → Personalization → Application**

No paid LLM API is required. Company, project, CV, and application data are persisted in **Supabase Postgres**.

---

## ✨ What CareerPlus Does

CareerPlus supports two complementary types of company queries.

### Structured company queries

For deterministic conditions, the agent uses database filtering directly.

```text
"Find French companies with fewer than 20 employees."
```

→ PostgreSQL filter

### Semantic company discovery

For conceptual queries, the system searches company descriptions using hybrid retrieval.

```text
"Find companies working on RAG solutions for healthcare."
```

→ Dense retrieval + BM25 + RRF + reranking

This distinction is intentional:

> **Use the database for deterministic constraints, RAG for semantic discovery, and the LLM for reasoning and personalization.**

---

# 🚀 Key Features

- 🤖 **Agentic AI** — local Qwen3 8B agent with tool calling and ReAct orchestration
- 🏢 **Company Intelligence** — structured company search and deterministic filtering
- 🔎 **Hybrid RAG** — dense retrieval + BM25 + Reciprocal Rank Fusion + cross-encoder reranking
- 🧠 **Semantic Company Discovery** — search companies by meaning rather than exact keywords
- 🌐 **LinkedIn Intelligence** — retrieve recent job postings using Playwright
- 📊 **Structured Results** — return matching companies as reusable datasets
- 🧩 **Project Knowledge Base** — retrieve relevant projects for each company
- 📄 **CV Selection** — select an existing CV version based on company relevance
- ✉️ **Personalized Applications** — generate company-specific spontaneous application emails
- 🔐 **Confirmation Before Sending** — email transmission requires explicit user confirmation
- 🗃️ **Application Tracking** — store sent applications and metadata in Supabase
- 🛡️ **Grounded Generation** — company, project, CV, and contact information must come from trusted sources
- 🔭 **Agent Observability** — tool calls and agent steps are traceable
- 🧱 **Clean Architecture** — domain logic remains independent from infrastructure

---

# 🧠 System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │   Streamlit UI  │
                  └────────┬────────┘
                           │ HTTP
                           ▼
                  ┌─────────────────┐
                  │  FastAPI API    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ AssistantService│
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ CareerPlusAgent │
                  │   Qwen3 8B      │
                  │ ReAct + Tools   │
                  └────────┬────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
   Structured DB      Hybrid Retrieval    LinkedIn
      Tools              Pipeline         Scraper
          │                │                 │
          │          ┌─────┴─────┐           │
          │          │           │           │
          │        Dense        BM25         │
          │          │           │           │
          │          └─────┬─────┘           │
          │                ▼                 │
          │              RRF                 │
          │                │                 │
          │           Reranking              │
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                  Company Intelligence
                           │
                           ▼
                  Structured Dataset
                           │
                           ▼
             ┌─────────────────────────┐
             │ Application Preparation│
             └────────────┬────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       Project Knowledge          CV Versions
             Base                      │
              │                        │
              └───────────┬────────────┘
                          ▼
                  Email Generation
                          │
                          ▼
                   User Confirmation
                          │
                          ▼
                      Gmail API
                          │
                          ▼
                  Application Tracker
```

---

# 🔍 Retrieval Strategy

CareerPlus uses different retrieval mechanisms depending on the query.

## 1. Deterministic filtering

Queries such as:

```text
Companies in France
Companies with fewer than 20 employees
Companies founded after 2020
```

are handled directly by PostgreSQL.

```text
User Query
    ↓
Agent
    ↓
Structured Tool
    ↓
Parameterized SQL
    ↓
Company Dataset
```

This avoids unnecessary LLM reasoning.

---

## 2. Semantic retrieval

Queries such as:

```text
Companies developing RAG solutions for healthcare
```

require understanding the meaning of company descriptions.

CareerPlus uses:

```text
Query
  ↓
BGE-M3 Embedding
  ↓
FAISS Dense Search
  +
BM25 Lexical Search
  ↓
RRF Fusion
  ↓
Cross-Encoder Reranking
  ↓
Relevant Companies
```

Current retrieval pipeline:

- **Dense:** `BAAI/bge-m3`
- **Lexical:** BM25Okapi
- **Fusion:** Reciprocal Rank Fusion, `k=60`
- **Reranker:** `BAAI/bge-reranker-v2-m3`

---

# 🤖 Agentic Layer

The agent uses a **ReAct-style loop** with local Qwen3 8B.

It receives the user request, determines the required action, calls tools, observes their results, and produces the final response.

The agent can decide between:

```text
Structured database query
Semantic retrieval
Company lookup
LinkedIn scraping
Project retrieval
CV selection
Email preparation
Email sending
```

The agent is constrained by tool schemas and system-level rules.

### Tool Registry

Tools are instantiated lazily through a schema-driven registry.

```text
CareerPlusAgent
      │
      ▼
 ToolRegistry
      │
 ┌────┼─────────────────────────────┐
 ▼    ▼     ▼       ▼       ▼       ▼
DB   RAG  LinkedIn Projects  CV    Gmail
```

---

# 🏢 Company Intelligence

Company records are stored in Supabase Postgres.

Each company can contain:

| Field          | Description               |
| -------------- | ------------------------- |
| `company_id`   | Unique identifier         |
| `name`         | Company name              |
| `domain`       | Company domain / activity |
| `website`      | Website                   |
| `founded_year` | Year founded              |
| `size`         | Number of employees       |
| `description`  | Company activity          |
| `contacts`     | Available email contacts  |
| `country`      | Country                   |

The company description is also indexed for semantic retrieval.

---

# 📊 Example: Company Discovery

### User

> Find companies working on RAG for healthcare.

### Agent

```text
semantic_company_search("RAG healthcare")
```

### Retrieval

```text
Query
 ↓
BGE-M3
 ↓
FAISS top-K
 +
BM25 top-K
 ↓
RRF
 ↓
Cross-Encoder
 ↓
Relevant Companies
```

### Result

The system returns a structured dataset containing fields such as:

| Company   | Domain        | Country | Size | Description | Contact     |
| --------- | ------------- | ------- | ---: | ----------- | ----------- |
| Company A | AI / RAG      | France  |   15 | ...         | contact@... |
| Company B | Healthcare AI | France  |    8 | ...         | hello@...   |

The dataset can then be reused by the application workflow.

---

# 📄 Project Knowledge Base

CareerPlus does not ask the LLM to interpret the CV itself.

Instead, projects are stored separately in a structured knowledge base.

Each project contains information such as:

```text
Project
├── Name
├── Short description
├── Detailed description
├── Technologies
├── Domain
├── AI / ML / RAG concepts
├── Skills demonstrated
└── Relevant keywords
```

Example:

```text
PaperLens

Domain:
RAG / Document Intelligence

Technologies:
Python, Qdrant, BM25, RRF, Qwen3, PyMuPDF

Relevant concepts:
RAG, Information Retrieval, LLM Engineering,
Document AI
```

This allows the application workflow to select projects based on the company's actual activity.

---

# 📑 Intelligent CV Selection

CareerPlus supports multiple existing CV versions.

A CV version is associated with a particular collection of projects.

For example:

```text
CV_RAG
├── PaperLens
├── Extraction Tool
└── CareerPulse

CV_ML
├── DataKit
├── Federated Fraud Detection
└── CareerPulse
```

The system determines:

```text
Company
   ↓
Company Activity
   ↓
Relevant Projects
   ↓
Matching CV Version
```

The LLM **never creates or modifies a CV**.

It only selects an existing version.

---

# ✉️ Personalized Spontaneous Applications

After discovering companies, the user can ask CareerPlus to prepare applications.

Example:

> Prepare an application for Company X.

The workflow is:

```text
Company
   ↓
Company Description
   ↓
Relevant Projects
   ↓
CV Selection
   ↓
Email Template
   ↓
Personalized Email
   ↓
User Review
```

The generated email is based only on information available in:

- the company database
- the project knowledge base
- the selected CV metadata
- the predefined email template

The LLM must not invent projects, technologies, achievements, or company information.

---

# 📧 Email Sending

Sending is deliberately separated from email generation.

```text
Prepare Application
        ↓
Generate Draft
        ↓
Show Preview
        ↓
USER CONFIRMATION
        ↓
Gmail API
        ↓
Successful Send
        ↓
Record Application
```

This prevents the agent from autonomously sending applications without user approval.

---

# 🗃️ Application Tracking

Successfully sent applications are persisted in Supabase.

Example:

```json
{
  "company": "Example AI",
  "contact": "contact@example.com",
  "cv_id": "cv_rag_01",
  "sent_at": "2026-09-20T14:30:00",
  "message_id": "gmail-message-id"
}
```

The application table contains:

| Field      | Purpose                   |
| ---------- | ------------------------- |
| Company    | Company name              |
| Contact    | Recipient                 |
| CV ID      | CV version sent           |
| Sent At    | Sending timestamp         |
| Message ID | Email provider identifier |

Additional metadata can be added for application status and follow-up workflows.

---

# 🌐 LinkedIn Intelligence

The existing LinkedIn scraping capability is exposed as an agent tool.

Example:

> Does Company X have recent AI Engineer openings?

The agent can invoke:

```text
scrape_linkedin(
    job_title="AI Engineer",
    company_names=["Company X"]
)
```

The Playwright-based scraper retrieves relevant LinkedIn job postings and returns the extracted information to the agent.

---

# 🧰 Agent Tools

| Tool                      | Type     | Purpose                                   |
| ------------------------- | -------- | ----------------------------------------- |
| `search_companies`        | Read     | Structured company search                 |
| `filter_companies`        | Read     | Deterministic filtering                   |
| `get_company`             | Read     | Retrieve a company                        |
| `get_company_contacts`    | Read     | Retrieve company contacts                 |
| `semantic_company_search` | RAG      | Semantic search over company descriptions |
| `scrape_linkedin`         | External | Retrieve recent LinkedIn jobs             |
| `get_projects`            | Read     | Retrieve relevant projects                |
| `select_cv`               | Read     | Select an existing CV                     |
| `prepare_application`     | Prepare  | Generate an application draft             |
| `send_email`              | Action   | Send and record an application            |

---

# 🛡️ Grounding & Safety Rules

CareerPlus enforces the following rules at both the prompt and application layers:

1. Never invent company information.
2. Never invent contact information.
3. Never invent projects, skills, or achievements.
4. Never generate or modify a CV.
5. Deterministic queries must use database filtering.
6. Semantic company discovery must use retrieval.
7. LLM reasoning must be grounded in retrieved evidence.
8. Application emails must use verified company/contact data.
9. Email sending requires explicit user confirmation.
10. Applications are recorded only after successful sending.

---

# 🏗️ Clean Architecture

The project separates business logic from infrastructure.

| Layer             | Responsibility                                        |
| ----------------- | ----------------------------------------------------- |
| `domain/`         | Entities, value objects and ports                     |
| `application/`    | Business use cases                                    |
| `infrastructure/` | Database, retrieval, Gmail, LinkedIn and LLM adapters |
| `agent/`          | ReAct loop, state and tool orchestration              |
| `tools/`          | Agent-facing tool interfaces                          |
| `api/`            | FastAPI HTTP interface                                |
| `services/`       | Dependency wiring and composition                     |
| `main.py`         | Composition root                                      |

The domain layer has no infrastructure dependency.

External technologies are accessed through adapters and ports, making components replaceable.

---

# 📁 Project Structure

```text
careerplus/
│
├── main.py
├── config.py
├── streamlit_app.py
├── requirements.txt
│
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── ports/
│   └── exceptions.py
│
├── application/
│   ├── search_companies.py
│   ├── filter_companies.py
│   ├── semantic_company_search.py
│   ├── prepare_application.py
│   └── send_application.py
│
├── infrastructure/
│   ├── storage/
│   ├── retrieval/
│   ├── email/
│   ├── scraping/
│   └── llm/
│
├── agent/
│   ├── agent.py
│   ├── state.py
│   ├── prompts.py
│   └── tool_registry.py
│
├── tools/
│   ├── search_companies_tool.py
│   ├── filter_companies_tool.py
│   ├── get_company_tool.py
│   ├── semantic_company_search_tool.py
│   ├── scrape_linkedin_tool.py
│   ├── get_projects_tool.py
│   ├── select_cv_tool.py
│   ├── generate_application_email_tool.py
│   └── send_email_tool.py
│
├── api/
│   ├── routes.py
│   ├── schemas.py
│   └── dependencies.py
│
├── services/
│   └── assistant_service.py
│
├── data/
│   └── faiss/
│
└── tests/
```

---

# 🗄️ Database Schema

CareerPlus uses four main Supabase tables:

| Table          | Purpose                  |
| -------------- | ------------------------ |
| `companies`    | Company intelligence     |
| `projects`     | Project knowledge base   |
| `cvs`          | Existing CV versions     |
| `applications` | Sent application records |

### Relationships

```text
companies
    │
    └──────────────► applications
                           │
                           ▼
                          cvs

projects ────────────────► cvs
```

---

# 🛠️ Technology Stack

| Component         | Technology                         |
| ----------------- | ---------------------------------- |
| Language          | Python 3.11+                       |
| Agent             | Custom ReAct + Ollama tool calling |
| LLM               | Qwen3 8B                           |
| LLM Runtime       | Ollama                             |
| Embeddings        | `BAAI/bge-m3`                      |
| Reranker          | `BAAI/bge-reranker-v2-m3`          |
| Dense Retrieval   | FAISS                              |
| Lexical Retrieval | BM25Okapi                          |
| Fusion            | Reciprocal Rank Fusion             |
| Database          | Supabase / PostgreSQL              |
| Scraping          | Playwright                         |
| Email             | Gmail API                          |
| Backend           | FastAPI + Uvicorn                  |
| Frontend          | Streamlit                          |
| Configuration     | Pydantic Settings                  |

---

# 📊 Observability

CareerPlus provides visibility into the agent's execution:

- JSON backend logs
- Agent step tracing
- Tool-call tracing
- Tool results displayed in the UI
- Health endpoint
- Application timestamps
- Gmail message IDs

This makes it possible to inspect **what the agent did and which tools were used** for a response.

---

# 🚀 Getting Started

## Prerequisites

- Python 3.11+
- Ollama
- Supabase project
- Gmail API credentials — optional, only required for sending emails

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd careerplus
```

---

## 2. Create the virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 4. Install and start Ollama

Pull the local model:

```bash
ollama pull qwen3:8b
```

Start Ollama:

```bash
ollama serve
```

---

## 5. Configure Supabase

Create a Supabase project and configure the required tables:

```text
companies
projects
cvs
applications
```

Add the following environment variables:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres

OLLAMA_MODEL=qwen3:8b
OLLAMA_HOST=http://localhost:11434

EMBEDDING_MODEL=BAAI/bge-m3
RERANKER_MODEL=BAAI/bge-reranker-v2-m3

ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

> Keep `.env`, OAuth tokens and credentials out of version control.

---

## 6. Populate the database

Add companies, projects and CV metadata to Supabase.

Example:

```sql
INSERT INTO companies (
    company_id,
    name,
    domain,
    website,
    founded_year,
    size,
    description,
    contacts,
    country
)
VALUES (
    'comp_001',
    'Example AI',
    'RAG / Information Retrieval',
    'https://example-ai.com',
    2019,
    15,
    'Example AI builds RAG systems for enterprise document search.',
    ARRAY['contact@example-ai.com'],
    'France'
);
```

---

## 7. Configure Gmail — Optional

If email sending is enabled, provide the required Gmail OAuth credentials.

Do not commit:

```text
credentials.json
token.json
.env
```

---

## 8. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

---

## 9. Start the frontend

In another terminal:

```bash
streamlit run streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

---

# 💬 Example Usage

### Company information

```text
What does Example AI do?
```

```text
get_company
      ↓
Company description
      ↓
Grounded LLM response
```

### Structured filtering

```text
Find French companies with fewer than 20 employees.
```

```text
filter_companies
      ↓
PostgreSQL
      ↓
Company dataset
```

### Semantic discovery

```text
Find companies working on RAG for healthcare.
```

```text
semantic_company_search
      ↓
FAISS + BM25
      ↓
RRF
      ↓
Cross-Encoder
      ↓
Relevant companies
```

### LinkedIn search

```text
Show me recent AI Engineer roles at Example AI.
```

```text
scrape_linkedin
      ↓
Playwright
      ↓
LinkedIn results
```

### Application

```text
Prepare a spontaneous application for Example AI.
```

```text
get_company
      ↓
get_projects
      ↓
select_cv
      ↓
prepare_application
      ↓
USER CONFIRMATION
      ↓
send_email
      ↓
application recorded
```

---

# 🔮 Roadmap

- [ ] Export filtered companies to CSV / Excel
- [ ] Conversation persistence
- [ ] Application history tool
- [ ] Application status tracking
- [ ] Automatic email-reply classification
- [ ] Retrieval evaluation dashboard
- [ ] Live company reindexing
- [ ] Additional job boards
- [ ] Multi-language application templates
- [ ] Contact validation
- [ ] More advanced company ranking
- [ ] Retrieval and agent latency metrics

---

## 🎯 Project Focus

CareerPlus brings together:

**Agentic AI + Hybrid RAG + Company Intelligence + Information Retrieval + Application Automation**

to build an end-to-end system for discovering relevant companies and turning company intelligence into personalized, traceable spontaneous applications.
