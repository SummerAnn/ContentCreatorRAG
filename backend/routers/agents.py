from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Globals will be injected
embedding_engine = None
vector_store = None
llm_backend = None

def set_globals(emb, vs, llm):
    global embedding_engine, vector_store, llm_backend
    embedding_engine = emb
    vector_store = vs
    llm_backend = llm

# Store agents in a simple JSON file (can be upgraded to database later)
AGENTS_FILE = "data/agents.json"

class Agent(BaseModel):
    id: Optional[str] = None
    name: str
    platform: str
    niche: str
    goal: str
    description: Optional[str] = None
    brand_voice: Optional[Dict] = None
    created_at: Optional[str] = None

class CreateAgentRequest(BaseModel):
    name: str
    platform: str
    niche: str
    goal: str
    description: Optional[str] = None
    brand_voice: Optional[Dict] = None

def load_agents() -> List[Dict]:
    """Load all agents from file"""
    if not Path(AGENTS_FILE).exists():
        return []
    try:
        with open(AGENTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading agents: {e}")
        return []

def save_agents(agents: List[Dict]):
    """Save agents to file"""
    Path(AGENTS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(AGENTS_FILE, 'w') as f:
        json.dump(agents, f, indent=2)

@router.get("/")
async def list_agents():
    """Get all agents"""
    agents = load_agents()
    return {"agents": agents}

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent"""
    agents = load_agents()
    agent = next((a for a in agents if a.get('id') == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/")
async def create_agent(req: CreateAgentRequest):
    """Create a new agent"""
    import uuid
    from datetime import datetime
    
    agents = load_agents()
    
    new_agent = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "platform": req.platform,
        "niche": req.niche,
        "goal": req.goal,
        "description": req.description,
        "brand_voice": req.brand_voice or {},
        "created_at": datetime.now().isoformat()
    }
    
    agents.append(new_agent)
    save_agents(agents)
    
    logger.info(f"Created agent: {new_agent['id']} - {new_agent['name']}")
    return new_agent

@router.put("/{agent_id}")
async def update_agent(agent_id: str, req: CreateAgentRequest):
    """Update an existing agent"""
    agents = load_agents()
    agent_index = next((i for i, a in enumerate(agents) if a.get('id') == agent_id), None)
    
    if agent_index is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agents[agent_index].update({
        "name": req.name,
        "platform": req.platform,
        "niche": req.niche,
        "goal": req.goal,
        "description": req.description,
        "brand_voice": req.brand_voice or {}
    })
    
    save_agents(agents)
    return agents[agent_index]

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    agents = load_agents()
    agents = [a for a in agents if a.get('id') != agent_id]
    save_agents(agents)
    return {"status": "deleted", "agent_id": agent_id}

