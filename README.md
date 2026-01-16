# ClickPost Assignment - Omni-Retail Multi-Agent Orchestrator

A production-grade hierarchical multi-agent orchestrator system that intelligently coordinates 4 specialized AI agents to provide seamless customer support across an e-commerce ecosystem.

## Features

- **Hierarchical Agent Coordination**: 1 Super Agent + 4 Specialized Sub-Agents
- **Real-time Voice Interaction**: Google ADK integration with low-latency streaming
- **Multi-Database Query Resolution**: Automatically routes and synthesizes data from 4 independent PostgreSQL databases
- **Dependency Management**: Intelligently resolves data dependencies between agents
- **Production-Ready**: Deployable on Google Cloud, with monitoring and scaling built-in

## Architecture

```
┌─────────────────────────────────────────┐
│    Super Agent (Orchestrator)           │
│  - LangGraph State Management           │
│  - Dependency Resolution                │
│  - Result Synthesis                     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┬──────────┐
       │       │       │          │
       ▼       ▼       ▼          ▼
   ┌────────┐┌───────┐┌────────┐┌────────┐
   │ShopCore││Ship   ││PayGuard││CareDesk│
   │Agent   ││Stream ││Agent   ││Agent   │
   │        ││Agent  ││        ││        │
   └────┬───┘└────┬───┘└────┬───┘└────┬───┘
        │         │         │         │
        └─────────┼─────────┼─────────┘
                  │
          ┌───────▼─────────┐
          │  Neon Database  │
          │  PostgreSQL     │
          │  (Serverless)   │
          └─────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | LangGraph | Agent coordination & state management |
| **Voice/AI** | Google ADK + Gemini 2.0 Flash | Real-time voice interaction |
| **Database** | Neon PostgreSQL + pgvector | Serverless storage with vector search |
| **Backend API** | FastAPI + Python 3.11 | REST/WebSocket API endpoints |
| **Frontend** | Next.js 15 + React + TypeScript | Chat & voice interfaces |
| **Deployment** | Docker + Vercel + Cloud Run | Containerization & scaling |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Neon PostgreSQL account
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DevXSoni021/ClickPost.git
cd ClickPost
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Install backend dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access Points

- **Home**: http://localhost:3000
- **Chat**: http://localhost:3000/chat
- **Voice**: http://localhost:3000/voice
- **Dashboard**: http://localhost:3000/dashboard
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
omni-retail-agent/
├── backend/
│   ├── agents/                # Sub-agent implementations
│   ├── orchestrator/          # Multi-agent coordination
│   ├── database/              # Database connections
│   ├── api/                   # FastAPI routes
│   └── voice/                 # Voice integration
├── frontend/
│   ├── app/                   # Next.js pages
│   └── components/            # Reusable components
├── scripts/                   # Database initialization
├── tests/                     # Unit tests
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API Endpoints

### REST API

- `POST /query` - Process multi-agent query
- `GET /health` - Health check
- `GET /agents/status` - Agent monitoring
- `GET /conversation-history` - Conversation history

### WebSocket Endpoints

- `ws://localhost:8000/ws/chat` - Real-time chat
- `ws://localhost:8000/ws/voice` - Voice interaction

## Testing

```bash
pytest tests/ -v
```

## Deployment

### Docker Compose

```bash
docker-compose up -d
```

### Google Cloud Run

```bash
gcloud run deploy omni-retail-backend \
  --source . \
  --region us-central1 \
  --platform managed
```

## License

MIT License

## Author

Devashish Soni