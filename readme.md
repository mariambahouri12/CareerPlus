# CareerPulse

CareerPulse is an AI-powered career assistant designed to help users discover, search, and manage job opportunities.

The platform combines LinkedIn job scraping, hybrid Retrieval-Augmented Generation (RAG), CV–job matching, and an AI agent capable of routing user requests to the appropriate workflow.

## Features

- 🔎 LinkedIn job scraping
- 🧠 Hybrid job search using semantic and lexical retrieval
- 🤖 AI agent with tool calling
- 📄 CV–job matching
- 📧 Automated email sending through the Gmail API
- 📝 Automatic application tracking
- 🔄 Application status management
- 💬 AI assistant for questions about scraped job offers
- 💻 Local LLM inference using Ollama

## Architecture

The system is organized around several components:

### Job Scraping

A LinkedIn scraping tool collects job offers based on:

- Job title
- Keywords
- Company filters

Scraped offers are automatically indexed for later retrieval.

### Hybrid RAG

CareerPulse combines:

- Dense semantic retrieval using BGE-M3 embeddings
- Lexical retrieval using BM25
- FAISS vector search
- Cross-encoder reranking

This allows users to ask natural-language questions about previously scraped job offers.

### AI Agent

The AI agent uses tool calling to select the appropriate workflow:

- `scrape_jobs` → discover new LinkedIn job offers
- `search_jobs` → search already indexed offers
- `send_email` → send an application email

The agent decides which tool should be executed based on the user's request.

### Automated Applications

When an application email is successfully sent, CareerPulse records the application with:

- Company
- Recipient email
- Date of application
- Application type (spontaneous or job-specific)
- Application status

Application data is stored locally.

## Technologies

- Python
- FastAPI
- Streamlit
- Ollama
- Qwen3
- Sentence Transformers
- BGE-M3
- FAISS
- BM25
- Cross-Encoder
- Gmail API
- Playwright

## API

The backend exposes REST endpoints through FastAPI.

Main endpoints:

```text
GET  /api/v1/health
POST /api/v1/chat
POST /api/v1/search-jobs
POST /api/v1/send-email
```
