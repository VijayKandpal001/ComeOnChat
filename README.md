# ComeOnChat

![ComeOnChat](https://img.shields.io/badge/chatbot-RAG%20AI-blue)

ComeOnChat is a Python-based intelligent chatbot application with a Streamlit UI, FastAPI backend, LangGraph orchestration, and PDF retrieval-augmented generation (RAG). It lets users chat with an assistant, manage conversation threads, upload PDF documents, and answer questions using ingested content.

---

## 🚀 Highlights

- **FastAPI backend** with REST endpoints for chat, streaming responses, PDF upload, and thread metadata.
- **Streamlit frontend** for live chat experience with thread selection and PDF indexing.
- **RAG support** using FAISS + Google Generative AI embeddings for document-aware answers.
- **Tool-enabled assistant** with search, calculator, stock lookup, and PDF retrieval tools.
- **Thread persistence** with SQLite checkpointing via LangGraph.

---

## 🧩 Architecture Overview

1. `frontend.py` starts a Streamlit app that communicates with the backend API.
2. `api.py` serves chat and PDF upload routes using FastAPI.
3. `backend/graph.py` builds a LangGraph chat flow using `ChatGroq` and custom tools.
4. `backend/rag.py` ingests PDFs, creates FAISS retrievers, and serves document context to the model.
5. `backend/memory.py` tracks thread metadata and available conversations.
6. `comeonchat.db` stores session state checkpoints for each thread.

---

## ✨ Features

- Create and switch between multiple chat threads
- Upload a PDF and ask questions about its content
- Stream chat responses from the API
- Auto-generate thread titles from conversation history
- Use built-in tools for web search, calculations, stock pricing, and RAG

---

## 📁 Repository Structure

- `api.py` – FastAPI application and route definitions
- `frontend.py` – Streamlit chat UI
- `backend/graph.py` – LLM graph, tool bindings, and chat logic
- `backend/rag.py` – PDF ingestion, vector store, and retrieval tool
- `backend/memory.py` – thread metadata and session helpers
- `Dockerfile.api` – Docker build for API service
- `Dockerfile.frontend` – Docker build for frontend UI
- `requirements.txt` – Python dependencies

### 🗂 File Architecture

```text
ComeOnChat/
├── api.py
├── frontend.py
├── Dockerfile.api
├── Dockerfile.frontend
├── requirements.txt
├── .env
├── comeonchat.db
└── backend/
    ├── __init__.py
    ├── graph.py
    ├── memory.py
    └── rag.py
```

---

## ⚙️ Prerequisites

- Python 3.12
- `pip`
- `docker` (optional, for container deployment)
- Valid API keys for external services

---

## 🔐 Required Environment Variables

Create a `.env` file with the following values:

```env
GROQ_API_KEY=<your-groq-api-key>
GOOGLE_API_KEY=<your-google-api-key>
LANGCHAIN_API_KEY=<your-langchain-api-key>
LANGCHAIN_ENDPOINT=<your-langchain-endpoint>
LANGCHAIN_PROJECT=<your-langchain-project>
LANGCHAIN_TRACING_V2=true
ALPHA_VANTAGE_API_KEY=<your-alpha-vantage-key>
API_URL=http://localhost:8000
```

> Keep secrets out of source control and do not commit `.env` with real credentials.

---

## 🧪 Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## ▶️ Run Locally

### Start the backend API

```powershell
$env:PORT=8000
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Start the frontend UI

```powershell
$env:PORT=8501
streamlit run frontend.py --server.address 0.0.0.0 --server.port 8501
```

Open the UI at `http://localhost:8501`.

---

## 🐳 Docker Deployment

### API container

```powershell
docker build -f Dockerfile.api -t comeonchat-api .
docker run -p 8000:8000 --env-file .env comeonchat-api
```

### Frontend container

```powershell
docker build -f Dockerfile.frontend -t comeonchat-frontend .
docker run -p 8501:8501 --env-file .env comeonchat-frontend
```

---

## 📌 API Endpoints

- `GET /` — health check
- `POST /chat` — send a chat message
- `POST /chat/stream` — receive streamed response chunks
- `POST /upload-pdf` — upload a PDF for indexing
- `GET /thread/{thread_id}/metadata` — retrieve PDF metadata for a thread
- `GET /threads` — list available thread IDs
- `GET /thread/{thread_id}/messages` — fetch chat history
- `GET /thread/{thread_id}/title` — generate a title for the thread
- `GET /thread/{thread_id}` — fetch full thread data and metadata

---

## 💡 Usage

1. Open the Streamlit UI.
2. Start a new chat or select an existing thread.
3. Upload a PDF document to enable RAG-powered answers.
4. Type your message and receive responses from the assistant.
5. Use the sidebar to browse thread history and document metadata.

---

## 🧰 Tech Stack

- Python 3.12
- FastAPI for the backend API
- Streamlit for the frontend UI
- LangGraph for chat graph orchestration and state management
- LangChain and LangChain Core for LLM interaction
- GROQ model via `langchain-groq`
- Google Generative AI embeddings via `google-genai`/`langchain-google-genai`
- FAISS for vector search and retrieval
- SQLite for session checkpoint storage
- Pydantic for request validation and structured output
- PDF parsing via `PyPDFLoader`
- Docker for containerized deployment

---

## 🚧 Troubleshooting

- If the frontend cannot connect, ensure `API_URL` points to your running backend.
- For PDF indexing failures, verify the uploaded file is a valid PDF.
- If the model does not respond, ensure your API keys are valid and environment variables are loaded.

---

## 💬 Extending ComeOnChat

You can enhance the project by:

- Adding support for more file types (Word, TXT, HTML)
- Replacing the LLM model with another provider
- Persisting thread data in a more scalable database
- Adding user authentication and access control
- Improving the UI with richer chat history presentation

---

## 📚 Credits

Built using FastAPI, Streamlit, LangGraph, LangChain, FAISS, and Google Generative AI.
