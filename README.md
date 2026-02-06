---

# Temporal RAG Agent – POC

This repository is a **proof of concept (POC)** demonstrating how **Temporal** can be used to orchestrate a **Retrieval-Augmented Generation (RAG) agent** with reliable execution, retries, and workflow visibility.

---

## Overview

* Temporal **workflows** manage the agent execution flow
* Temporal **activities** handle the actual RAG logic
* Automatic **retry and failure handling**
* **FastAPI** is used to trigger workflows
* Execution can be monitored using **Temporal UI**

---

## Architecture

FastAPI → Temporal Workflow → Temporal Activities → RAG Agent

---

## Project Structure

```
temporal-rag_agent/
├── rag_agent/
│   ├── agent.py          # Core RAG agent logic
│   ├── tools.py          # Retrieval and helper tools
│   ├── workflows/        # Temporal workflows
│   ├── activities/       # Temporal activities
│   └── tests/
│
├── server.py             # FastAPI server (workflow trigger)
├── pyproject.toml
└── README.md
```

---

## Why Temporal?

* Reliable execution for long-running workflows
* Built-in retries and failure recovery
* Clear separation between orchestration and business logic
* Strong observability through Temporal UI

---

## Running Locally

### Prerequisites

* Python 3.10+
* Temporal Server (local or remote)
* `uv` or `pip`

---

### Steps (Run in Separate Terminals)

**Terminal 1 – Start the Temporal dev server**

```bash
temporal server start-dev
```

**Terminal 2 – Start the workflow trigger**

```bash
python start_workflow.py
```

**Terminal 3 – Start the Temporal worker**

```bash
python worker.py
```

> Ensure the Temporal server is running before starting the workflow and worker.

---

## Demo Flow

1. FastAPI server is started
2. Temporal worker listens for tasks
3. Workflow is triggered using `start_workflow.py`
4. Workflow executes RAG activities
5. Failures are retried automatically
6. Execution can be viewed in Temporal UI

---

## Notes

This project is a **POC** focused on showcasing Temporal-based orchestration for AI agents.

---
