# 🤖 Omni-Retail Multi-Agent Orchestrator

A high-performance, voice-enabled multi-agent support system designed for modern e-commerce. This platform uses a specialized **Planner-Orchestrator** architecture to handle complex user queries across multiple domains including order tracking, payment processing, and customer support.

---

## 🏗️ System Architecture

The project follows a **Multi-Agent Orchestration** pattern inspired by LangGraph principles, but optimized for deterministic transactional data.

### 🔄 Workflow Logic
When a user asks a question, the **Super Agent** acts as the high-level brain:
1.  **Analyze (Planner)**: Deconstructs the query to identify which specialized sub-agents (ShopCore, ShipStream, PayGuard, CareDesk) are needed.
2.  **Execute (Parallel stages)**: Runs agents in parallel where possible. For example, it can fetch tracking details and payment status simultaneously if the Order ID is already known.
3.  **Synthesis (Merger)**: Collects raw structured data from all agents and uses **Gemini 2.0 Flash** to weave a human-like narrative response.

```mermaid
graph TD
    User((User)) -->|Query| SuperAgent[Super Agent Orchestrator]
    SuperAgent -->|1. Plan| Planner{Planner Logic}
    
    Planner -->|Identifies Agents| Stage1[Stage 1: ShopCore]
    Stage1 -->|Resolves Order ID| Stage2[Stage 2: Parallel Execution]
    
    Stage2 --> Agent1[ShipStream Agent]
    Stage2 --> Agent2[PayGuard Agent]
    Stage2 --> Agent3[CareDesk Agent]
    
    Agent1 --> Merge[Result Merger]
    Agent2 --> Merge
    Agent3 --> Merge
    
    Merge -->|Structured Data| Synthesis[Gemini Synthesis]
    Synthesis -->|Narrative| User
    
    subgraph "Database Layer (Neon PostgreSQL)"
        DB1[(ShopCore DB)]
        DB2[(ShipStream DB)]
        DB3[(PayGuard DB)]
        DB4[(CareDesk DB)]
    end
    
    Stage1 -.-> DB1
    Agent1 -.-> DB2
    Agent2 -.-> DB3
    Agent3 -.-> DB4
```

---

## 🧠 Technical Deep-Dive

### 🛡️ Why Text-to-SQL instead of Embeddings/RAG?
For this specific project, we chose a **Deterministic Text-to-SQL** approach over a pure Vector/Embedding approach for several critical reasons:

1.  **Transactional Accuracy**: E-commerce data (order statuses, wallet balances, tracking numbers) requires 100% precision. Embeddings are probabilistic and can "hallucinate" similar-sounding but incorrect IDs.
2.  **Transitive Relations**: SQL allows us to perform complex JOINs across tables (e.g., Finding a Wallet ID via an Order ID by bridging through Transactions). This is highly efficient and difficult to achieve with flat vector lookups.
3.  **Real-Time Data**: Transactional databases update constantly. Maintaining a vector index in sync with millions of order updates is computationally expensive; direct SQL queries are instantaneous and always fresh.

### 🛠️ Tech Stack & Library Usage

| Module | Technology | Why we use it |
| :--- | :--- | :--- |
| **Backend** | FastAPI | Asynchronous performance and built-in WebSocket support for real-time voice/chat. |
| **Orchestrator** | Python / Asyncio | Handles the concurrent execution of multiple sub-agents without blocking the main thread. |
| **LLM** | Gemini 2.0 Flash | Used for high-level query analysis (intent detection) and final narrative synthesis. |
| **Database** | Neon (PostgreSQL) | Serverless Postgres that scales with our multi-agent load. |
| **Communication**| WebSockets | Enables seamless, low-latency interaction for both text and voice. |
| **Frontend** | Next.js / React | Provides a "Glassmorphic" premium UI with real-time state management. |

---

## 🚀 Key Features

*   **Uniform Agent Architecture**: Every agent inherits from a `BaseAgent`, ensuring a standardized way to extract parameters and generate SQL.
*   **Context Locking Prevention**: The orchestrator is smart enough to know when to stick to a previous order context and when to override it if you mention a new ID or product.
*   **Parallel Orchestration**: By identifying dependencies at the root, we can trigger independent sub-agents in a single parallel sweep, reducing latency by up to 60%.
*   **Session Reset**: Built-in support for "New Chat" functionality to wipe context and start fresh conversations.

---

## 🛠️ Setup & Installation

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/DevXSoni021/ClickPost.git
   cd ClickPost
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn api.main:app --reload
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

Developed with ❤️ for the Omni-Retail Ecosystem.