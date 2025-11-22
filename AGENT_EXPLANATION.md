# 🤖 How Agents Work in the Backend

## 📋 Current State

### ✅ What EXISTS:

1. **Agent Storage** (`backend/routers/agents.py`)
   - Agents stored in `data/agents.json` (JSON file)
   - When you "hire" an agent from template, creates entry:
   ```json
   {
     "id": "uuid",
     "name": "Chief Strategy Officer",
     "platform": "tiktok",
     "niche": "tech",
     "goal": "grow_followers",
     "system_prompt": "You are the Chief Strategy Officer...",  // Specialized prompt!
     "temperature": 0.7,
     "max_tokens": 2000,
     "capabilities": ["strategy_development", ...]
   }
   ```

2. **16 Agent Templates**
   - Strategy Team: CSO, Brand Strategist, Audience Researcher
   - Content Team: Creative Director, Copywriter, Script Writer, Editor
   - Creative Team: Hook Specialist, Thumbnail Designer
   - Analytics Team: Performance Analyst, Growth Hacker, A/B Tester
   - Distribution Team: Platform Optimizer, SEO Specialist, Community Manager
   - Leadership: Campaign Manager

3. **API Endpoints**
   - `GET /api/agents/` - List all agents
   - `GET /api/agents/{id}` - Get specific agent
   - `POST /api/agents/from-template` - Hire from template
   - `GET /api/agents/templates` - List all templates

### ❌ What's MISSING:

**Agents are NOT used in generation yet!**

The generation endpoints (`/api/generate/hooks`, `/api/generate/script`, etc.) use **generic prompts** from:
- `backend/prompts/hooks.py` → `HOOK_SYSTEM_PROMPT`
- `backend/prompts/scripts.py` → `SCRIPT_SYSTEM_PROMPT`
- etc.

They don't use the agent's specialized `system_prompt`.

---

## 🎯 How Agents SHOULD Work

### The Flow:

```
1. User hires agent (e.g., "Hook Specialist")
   ↓
2. Agent saved to data/agents.json with specialized system_prompt
   ↓
3. User selects agent in frontend
   ↓
4. Frontend sends agent_id in GenerateRequest
   ↓
5. Backend loads agent from data/agents.json
   ↓
6. Backend uses agent's system_prompt instead of generic one
   ↓
7. LLM generates content using agent's specialized personality/expertise
```

### Example:

**Current (Generic):**
```python
# backend/prompts/hooks.py
HOOK_SYSTEM_PROMPT = "You are HookMaster, an elite copywriter..."
messages = [
    {"role": "system", "content": HOOK_SYSTEM_PROMPT},  # Generic!
    {"role": "user", "content": user_prompt}
]
```

**With Agents (Should Be):**
```python
# Load agent
agent = load_agent(agent_id)
agent_system_prompt = agent["system_prompt"]  # "You are the Hook Specialist - master of stopping the scroll..."

messages = [
    {"role": "system", "content": agent_system_prompt},  # Agent's specialized prompt!
    {"role": "user", "content": user_prompt}
]
```

---

## 🔧 How to Integrate Agents into Generation

### Step 1: Add `agent_id` to GenerateRequest

```python
# backend/routers/generate.py
class GenerateRequest(BaseModel):
    user_id: str = "default_user"
    platform: str
    niche: str
    goal: str
    personality: str = "friendly"
    audience: List[str] = ["gen_z"]
    reference_text: Optional[str] = None
    reference_image: Optional[str] = None
    content_type: str
    options: dict = {}
    agent_id: Optional[str] = None  # NEW: Agent to use
```

### Step 2: Load Agent in Generation Endpoints

```python
@router.post("/hooks")
async def generate_hooks(req: GenerateRequest):
    # Load agent if provided
    agent = None
    system_prompt = HOOK_SYSTEM_PROMPT  # Default generic prompt
    
    if req.agent_id:
        agents = load_agents()
        agent = next((a for a in agents if a.get('id') == req.agent_id), None)
        if agent:
            system_prompt = agent.get("system_prompt", HOOK_SYSTEM_PROMPT)
            temperature = agent.get("temperature", 0.95)
            max_tokens = agent.get("max_tokens", 2000)
        else:
            logger.warning(f"Agent {req.agent_id} not found, using generic prompt")
    
    # Use agent's system_prompt instead of generic one
    messages = [
        {"role": "system", "content": system_prompt},  # Agent's specialized prompt!
        {"role": "user", "content": user_prompt}
    ]
    
    # Use agent's temperature if available
    temp = agent.get("temperature", 0.95) if agent else 0.95
    
    for chunk in llm_backend.generate_stream(messages, temperature=temp):
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
```

### Step 3: Match Agent to Content Type

Some agents are specialized:
- "Hook Specialist" → Use for `/hooks` endpoint
- "Script Writer" → Use for `/script` endpoint
- "Thumbnail Designer" → Use for `/thumbnails` endpoint

You could:
1. Auto-select agent based on content_type
2. Validate agent matches content_type
3. Use agent's capabilities to determine compatibility

---

## 🎨 Agent Capabilities by Content Type

| Agent | Best For | Content Types |
|-------|----------|---------------|
| Hook Specialist | Hooks | `hooks` |
| Script Writer | Scripts | `script` |
| Copywriter | Captions, CTAs | `cta`, `descriptions` |
| Thumbnail Designer | Thumbnails | `thumbnails` |
| SEO & Hashtag Specialist | Tags | `tags` |
| Creative Director | Ideas, Concepts | All (strategy) |
| Platform Optimizer | Optimization | All (post-processing) |

---

## 🚀 Future Enhancements

1. **Agent Chaining**: One agent generates content, another optimizes it
   - Hook Specialist → Platform Optimizer → SEO Specialist

2. **Agent Collaboration**: Multiple agents work together
   - Creative Director (ideas) → Script Writer (script) → Hook Specialist (hook) → Copywriter (caption)

3. **Agent Learning**: Agents learn from successful content
   - Store what worked well for each agent
   - Refine agent's system_prompt based on performance

4. **Agent-Specific RAG**: Each agent has their own RAG context
   - Hook Specialist searches for successful hooks
   - Script Writer searches for successful scripts

---

## 📝 Summary

**Current State:**
- ✅ Agents stored and managed
- ✅ 16 specialized agent templates
- ❌ Agents NOT used in generation (uses generic prompts)

**To Make Agents Work:**
1. Add `agent_id` to `GenerateRequest`
2. Load agent in generation endpoints
3. Use agent's `system_prompt` instead of generic one
4. Use agent's `temperature` and `max_tokens`
5. Match agent to content type

**The Power of Agents:**
Instead of one generic "HookMaster" prompt, you have 16 specialized agents:
- Hook Specialist → "master of stopping the scroll"
- Script Writer → "retention-optimized scripts"
- Copywriter → "persuasive, engaging copy"
- etc.

Each agent has their own personality, expertise, and approach!

