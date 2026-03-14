# ⚡ Quick Reference Guide

Your personal cheat sheet for the Skill-Based AI Agent project.

---

## 🎯 Project In One Picture

```
User Query
    ↓
SkillMatcher (LLM ranks skills)
    ↓
Check Script Execution (LLM decides)
    ↓
Build Messages (with skill instructions + history)
    ↓
Azure OpenAI (generate response)
    ↓
User sees response
```

---

## 🔑 Key Components

| Component | What it does | Key method |
|-----------|-------------|-----------|
| **SkillBasedAgent** | Orchestrates everything | `process_query()` |
| **SkillMatcher** | Ranks skills by relevance | `match_skills()` |
| **SkillLoader** | Discovers skills from disk | `get_all_skills()` |
| **AzureOpenAIClient** | Talks to Azure OpenAI | `chat_completion()` |
| **ScriptExecutor** | Runs Python scripts safely | `execute_python_script()` |

---

## 📊 Data Flow

```
User Input
    ↓
Skill Matching (800ms)
    ├─ Send query + skills to LLM
    └─ Get ranked list
    ↓
Script Detection (800ms, if executor skill matched)
    ├─ Ask LLM: "execute?"
    ├─ Parse response
    └─ Run script if yes
    ↓
Build Messages
    ├─ System prompt with skill instructions
    ├─ Conversation history (last 10)
    └─ Current query
    ↓
LLM Response (1000ms)
    ├─ Generate text
    └─ Stream if enabled
    ↓
User Response
    └─ Store in history
```

---

## 🧠 Core Concepts

### Skill Matching
```
Query: "Write Python code"
Available: Code Assistant (desc), Data Analysis (desc), Writing (desc)
LLM Decision: "1, 2" → Code Assistant + Data Analysis
```

### Script Execution
```
Query: "Calculate 5 times 3"
LLM Decides: "EXECUTE:calculator.py:multiply,5,3"
Agent Runs: python calculator.py multiply 5 3
Output Captured: "Result: 15.0"
LLM Explains: "5 × 3 = 15"
```

### Message Building
```
System Prompt
├─ Base instructions
├─ Skill 1 instructions (full SKILL.md)
├─ Skill 2 instructions (full SKILL.md)
└─ Script execution context (if applicable)

+ Conversation History (last 10 messages)

+ Current User Query

= Messages sent to Azure OpenAI
```

---

## ⚙️ Configuration

```env
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Choose one:
AZURE_OPENAI_API_KEY=key        # OR
AZURE_TENANT_ID=id
AZURE_CLIENT_ID=id
AZURE_CLIENT_SECRET=secret

# Optional
MAX_TOKENS=4000                 # Budget for response
TEMPERATURE=0.3                 # Lower = more consistent
SKILLS_DIRECTORY=./skills
LOG_LEVEL=INFO
```

---

## 📈 Typical Latency

```
Skill Matching:           ~800ms
Script Detection:         ~800ms (if applicable)
Script Execution:         ~500ms (if applicable)
Response Generation:     ~1000ms
─────────────────────────────
Total (no script):       ~1800ms (~2 seconds)
Total (with script):     ~2600ms (~3 seconds)
```

---

## 💾 Token Budget

```
Max Tokens: 4000

Typical Usage:
├─ System Prompt:        ~1200 (30%)
├─ Skill Instructions:   ~800  (20%)
├─ History (10 msgs):    ~1000 (25%)
├─ Current Query:        ~200  (5%)
└─ Response (max):       ~1300 (32%)
```

---

## 🛡️ Error Handling Philosophy

```
Try X
  └─ Success? Return
  └─ Fail? Try Y
     └─ Success? Return
     └─ Fail? Try Z
        └─ Success? Return
        └─ Fail? Continue with degradation
```

**Example:**
```
Try: Match skills
  Fail? → Continue without skills
Try: Execute script
  Fail? → Continue without output
Try: Generate response
  Fail? → Return error message
```

---

## 🔥 Interview Talking Points

### "The Key Innovation"
> "The system can automatically detect when Python scripts should run, execute them safely, and include the output in the LLM's context. This creates a seamless experience without users needing to manually run scripts."

### "Why LLM-Based Matching?"
> "Semantic understanding. Keyword matching would fail on ambiguous queries. Using the LLM to rank skills understands context better, even though it's slower."

### "Error Recovery"
> "Graceful degradation at each step. If skill matching fails, we process without skills. If script execution fails, we continue without output. The system always provides value."

### "Token Management"
> "We carefully balance token usage. Skill instructions are expensive but necessary. We keep last 10 messages for context but not more to avoid token exhaustion."

### "If Scaling to 1000s of Users"
> "Add async queue (Celery), persist to database (PostgreSQL), cache skills and summaries (Redis), use cheaper models for matching (GPT-3.5), implement prompt caching."

---

## 🧪 Quick Testing

```python
from core.agent import SkillBasedAgent

agent = SkillBasedAgent()

# Test 1: Simple query
response = agent.process_query(
    "What is the capital of France?",
    use_skills=False
)

# Test 2: With skills
response = agent.process_query(
    "Write a Python function to sort a list",
    use_skills=True
)

# Test 3: Streaming
for chunk in agent.process_query("Explain AI", stream=True):
    print(chunk, end="", flush=True)

# Test 4: Multi-turn
agent.process_query("Write a function")
agent.process_query("Now optimize it")  # Sees previous messages

# View history
history = agent.get_conversation_history()
print(f"Messages: {len(history)}")
```

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `agent.py` | Main orchestrator |
| `skill_matcher.py` | LLM-based skill ranking |
| `skill_loader.py` | Skill discovery |
| `azure_client.py` | Azure API wrapper |
| `tools.py` | Script execution |
| `config.py` | Configuration |
| `helpers.py` | Token counting, text utils |
| `logger.py` | Logging setup |
| `streamlit_app.py` | Web UI |
| `example.py` | CLI usage examples |

---

## 🎓 Key Equations

### Token Count
```
total_tokens = Σ tokens(each message)
Available for response = MAX_TOKENS - total_tokens
```

### Skill Match Quality
```
Quality = SemanticRelevance(Query, Skill)
         × Confidence(LLM parsing response)
```

### Latency
```
Total = SkillMatching + ScriptDetection + ResponseGeneration
      = 800ms + (800ms if executor) + 1000ms
```

---

## ⚠️ Common Gotchas

| Issue | Solution |
|-------|----------|
| "Skills not loading" | Check `skills/*/SKILL.md` exists |
| "Token limit exceeded" | Reduce history window (10 → 5) |
| "Script not executing" | Ensure `executor` skill matched |
| "Slow responses" | Add caching, use cheaper models |
| "API failures" | Implement retries + fallback models |
| "Memory leaks" | Clear history regularly |

---

## 🚀 Performance Tips

1. **Cache skill instructions** → Save 90% tokens
2. **Use cheaper models for matching** → GPT-3.5 vs GPT-4
3. **Implement message summarization** → Keep context, save tokens
4. **Batch user requests** → Amortize API overhead
5. **Add response caching** → For common queries

---

## 🔒 Security Checklist

- [ ] Scripts isolated to `skills/*/scripts/`
- [ ] Timeout enforced (30 seconds)
- [ ] Output captured safely (no direct terminal)
- [ ] File paths validated
- [ ] Arguments sanitized
- [ ] Error messages logged
- [ ] Rate limiting implemented
- [ ] Code review process for new scripts
- [ ] Static analysis on scripts
- [ ] No arbitrary code execution

---

## 📚 Documentation Files

| File | Contains |
|------|----------|
| `README.md` | Overview, installation, usage |
| `ARCHITECTURE.md` | Deep technical design |
| `INTERVIEW_GUIDE.md` | Q&A and talking points |
| `QUICK_REFERENCE.md` | This file! |

---

## 💡 30-Second Pitch

> "I built a Skill-Based AI Agent that intelligently routes queries to domain-specific skills and automatically executes Python scripts. The system uses LLM-based skill matching, automatic script detection, and multi-turn conversation management. It's inspired by Claude's skill architecture but built with Azure OpenAI."

---

## 2-Minute Pitch

> "The system has four main components:
>
> 1. **SkillMatcher** - Uses an LLM to intelligently rank available skills based on semantic understanding of the user's query
>
> 2. **SkillBasedAgent** - Orchestrates: matching skills, detecting if scripts should run, building messages with skill context, and generating responses
>
> 3. **ScriptExecutor** - Safely runs Python scripts with validation, timeout handling, and output capturing
>
> 4. **AzureOpenAIClient** - Handles authentication (API key or Azure AD) and communication with Azure OpenAI
>
> The innovation is automatic script execution detection - the system determines when to run scripts based on the query, executes them in isolation, and includes output in the LLM's context for interpretation. This creates a seamless experience where users don't manually run scripts."

---

## 🎯 Interview Preparation Checklist

- [ ] Read through README.md
- [ ] Study ARCHITECTURE.md for depth
- [ ] Prepare answers from INTERVIEW_GUIDE.md
- [ ] Run the code locally
- [ ] Practice 30-second and 2-minute pitches
- [ ] Prepare examples (write code, run script, etc.)
- [ ] Think about tradeoffs and improvements
- [ ] Be ready to discuss error handling
- [ ] Have answers for "what would you do differently?"
- [ ] Review the Quick Reference (this file)

---

**You've got this! 💪**
