from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.orchestrator.super_agent import OmniRetailSuperAgent
from pydantic import BaseModel
from typing import Optional, List
import json
import asyncio
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Omni-Retail Multi-Agent API",
    description="Voice-enabled multi-agent orchestrator for e-commerce",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global super agent instance
super_agent: Optional[OmniRetailSuperAgent] = None

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    user_id: Optional[int] = None
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    timestamp: str
    query: str
    agents_invoked: List[str]
    narrative_response: str
    data_sources: dict

class HealthResponse(BaseModel):
    status: str
    agents_initialized: bool
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize super agent on startup"""
    global super_agent
    print("🚀 Starting Omni-Retail API Server...")
    try:
        super_agent = OmniRetailSuperAgent()
        print("✓ Super Agent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Super Agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global super_agent
    if super_agent:
        super_agent.cleanup()
        print("✓ Super Agent cleanup complete")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        agents_initialized=super_agent is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process complex multi-agent query"""
    
    if not super_agent:
        raise HTTPException(status_code=503, detail="Super Agent not initialized")
    
    try:
        # Process query
        response = super_agent.process_complex_query(
            request.query,
            user_id=request.user_id
        )
        
        return QueryResponse(
            timestamp=response["timestamp"],
            query=response["original_query"],
            agents_invoked=response["agents_invoked"],
            narrative_response=response["narrative_response"],
            data_sources=response["data_sources"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all sub-agents"""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Super Agent not initialized")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "ShopCore": "ready",
            "ShipStream": "ready",
            "PayGuard": "ready",
            "CareDesk": "ready"
        },
        "conversation_history_length": len(super_agent.conversation_history)
    }

@app.get("/conversation-history")
async def get_conversation_history(user_id: Optional[int] = None):
    """Get conversation history"""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Super Agent not initialized")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "history_length": len(super_agent.conversation_history),
        "history": super_agent.conversation_history
    }

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue
            
            # Process query
            if super_agent and "query" in message:
                try:
                    response = super_agent.process_complex_query(
                        message["query"],
                        user_id=message.get("user_id")
                    )
                    
                    # Send response back to client
                    await websocket.send_json({
                        "type": "response",
                        "timestamp": response["timestamp"],
                        "narrative": response["narrative_response"],
                        "agents_used": response["agents_invoked"],
                        "data_sources": response["data_sources"]
                    })
                except Exception as e:
                    print(f"Error processing query: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing query: {str(e)}"
                    })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Missing 'query' field in message"
                })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass  # Connection might already be closed
    
    finally:
        try:
            await websocket.close()
        except:
            pass  # Connection might already be closed

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice interaction (Google ADK)"""
    await websocket.accept()
    
    try:
        while True:
            # Receive audio data or transcribed text
            data = await websocket.receive_json()
            
            if "transcription" in data:
                # Process transcribed text
                response = super_agent.process_complex_query(
                    data["transcription"],
                    user_id=data.get("user_id")
                )
                
                # Send response (will be converted to speech by client)
                await websocket.send_json({
                    "type": "voice_response",
                    "text": response["narrative_response"],
                    "timestamp": response["timestamp"]
                })
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    
    finally:
        await websocket.close()

# Run with: uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
