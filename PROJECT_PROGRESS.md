# GenRec-AI Development Progress

## Project

**GenRec-AI: Agentic AI Laboratory Record Generation System using RAG and MLOps**

GenRec-AI generates institution-specific laboratory records from observation notes, experiment details, notebooks, source code, screenshots, and other supporting evidence.

## Technology Stack

### Frontend

- Django Templates
- Tailwind CSS
- JavaScript
- Alpine.js
- Chart.js
- PDF.js

### Backend

- Django
- Django REST Framework

### AI and Agent Orchestration

- LangGraph
- LangChain
- Gemini API

### Retrieval-Augmented Generation

- ChromaDB
- Sentence Transformers

### OCR

- Tesseract OCR

### Database

- SQLite for development
- PostgreSQL planned for production

### MLOps

- GitHub
- GitHub Actions
- Docker
- DVC
- MLflow

## Planned Agents

1. Planner Agent
2. Observation Extraction Agent
3. Experiment Planning Agent
4. Retrieval Agent
5. Content Generation Agent
6. Experiment Evidence Agent
7. Validation Agent
8. Format Learning Agent
9. Document Generation Agent

## Completed Work

- Created the Django project.
- Created and activated a Python virtual environment.
- Installed Django and Django REST Framework.
- Created the following Django applications:
  - accounts
  - agents
  - api
  - documents
  - experiments
  - rag
  - mlops
- Configured SQLite as the development database.
- Configured static and media directories.
- Created the Experiment database model.
- Added fields for:
  - Subject
  - Experiment title
  - Aim
  - Theory
  - Algorithm
  - Procedure
  - Program
  - Output
  - Result
  - Generated record
  - Observation file
  - Generated PDF
  - Generated DOCX
  - Processing status
- Created and applied Django migrations.
- Registered the Experiment model in Django Admin.
- Created a Django superuser.
- Verified the Django Admin interface.
- Verified the backend server on port 8001.

## Current Backend URL

```text
http://127.0.0.1:8001/
