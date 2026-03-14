# 🤖 Skill-Based AI Agent

A sophisticated Python-based AI agent system that leverages **skill modules** and **automatic script execution** to provide specialized capabilities. Built with **Azure OpenAI** and inspired by Claude's skill system, this agent can intelligently match user queries to relevant skills and execute Python scripts autonomously.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Features](#core-features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Skills System](#skills-system)
- [Script Execution](#script-execution)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Interview Preparation](#interview-preparation)

---

## 📖 Overview

The **Skill-Based AI Agent** is an intelligent system that combines:

1. **Large Language Models (Azure OpenAI)** - For natural language understanding and generation
2. **Skill Modules** - Domain-specific instructions and guidelines
3. **Automatic Script Execution** - Runs Python scripts based on user requests
4. **Conversation Management** - Maintains context across multi-turn conversations

### Key Innovation

Unlike traditional chatbots, this agent:
- **Dynamically matches** user queries to relevant skills using LLM-based matching
- **Automatically detects and executes** Python scripts without user intervention
- **Maintains context** across conversation turns
- **Provides streaming responses** for better UX
- **Integrates skill instructions** directly into system prompts

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI (Web Interface)                 │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              SkillBasedAgent (Core Orchestrator)                │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Azure OpenAI    │  │  Skill Matcher   │  │ Script       │ │
│  │  Client          │  │  (LLM-based)     │  │ Executor     │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                              │                       │           │
└─────────────────────────────────────────────────────────────────┘
          │                    │                       │
          ▼                    ▼                       ▼
    ┌──────────┐          ┌──────────┐          ┌──────────┐
    │  Azure   │          │ Skill    │          │ Python   │
    │ OpenAI   │          │ Loader   │          │ Scripts  │
    │  API     │          │          │          │          │
    └──────────┘          └──────────┘          └──────────┘
                               │
                               ▼
                          ┌──────────┐
                          │ Skills/  │
                          │ *.md     │
                          └──────────┘
```

### Data Flow

```
User Query
    │
    ▼
[Agent.process_query()]
    │
    ├─→ Match Skills (SkillMatcher)
    │        │
    │        └─→ LLM ranks available skills
    │
    ├─→ Check Script Execution (Automatic Detection)
    │        │
    │        └─→ If python_executor skill matched:
    │            └─→ Execute Python script
    │            └─→ Capture output
    │
    └─→ Build Messages (with skill instructions)
         │
         └─→ Add matched skills to system prompt
         └─→ Add script output (if executed)
         └─→ Add conversation history
             │
             ▼
         [Azure OpenAI API]
             │
             ▼
         Generate Response
             │
             ▼
         [Stream or Return]
             │
             ▼
         User Interface
```

---

## ⚡ Core Features

### 1. **Intelligent Skill Matching**
- Queries are analyzed by LLM to find relevant skills
- Returns top 3 most relevant skills
- Fallback to first skill if matching fails
- Skills are included in system prompt

### 2. **Automatic Script Execution**
- Detects when Python scripts should run
- Validates script paths and arguments
- Captures stdout, stderr, and exit codes
- Formats and includes output in LLM context

### 3. **Multi-turn Conversation Management**
- Maintains conversation history (last 10 messages)
- Tracks context across interactions
- Supports clearing history for fresh starts
- Token counting and management

### 4. **Skill System**
- Modular skill definitions via `SKILL.md` files
- Skills contain domain-specific instructions
- Optional custom tools via `tools.py`
- Automatic skill discovery and loading

### 5. **Streaming Responses**
- Real-time response streaming for better UX
- Token-based message building
- Proper error handling during streaming

### 6. **Authentication**
- Supports Azure OpenAI API Key authentication
- Supports Azure AD token-based authentication
- Flexible credential management

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- pip or conda for package management

### Step 1: Clone or Extract Project

```bash
# Navigate to project directory
cd skill-based-agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `openai==1.54.0` - Azure OpenAI SDK
- `azure-identity==1.19.0` - Azure authentication
- `streamlit==1.39.0` - Web UI
- `tiktoken==0.8.0` - Token counting
- `python-dotenv==1.0.1` - Environment management

### Step 3: Setup Environment Variables

Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: Azure AD Authentication (alternative to API key)
# AZURE_TENANT_ID=your-tenant-id
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-secret

# Agent Settings
MAX_TOKENS=4000
TEMPERATURE=0.3

# Skills Directory (optional)
# SKILLS_DIRECTORY=./skills

# Logging
LOG_LEVEL=INFO
```

### Step 4: Verify Installation

```bash
python -c "from core.agent import SkillBasedAgent; print('✅ Installation successful')"
```

---

## ⚙️ Configuration

### Config File (`config.py`)

The agent loads configuration from environment variables:

```python
class Config:
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT      # Required
    AZURE_OPENAI_API_KEY       # API key OR Azure AD creds
    AZURE_OPENAI_DEPLOYMENT_NAME  # Default: "gpt-4"
    AZURE_OPENAI_API_VERSION   # Default: "2024-02-15-preview"
    
    # Agent
    MAX_TOKENS                 # Default: 4000
    TEMPERATURE                # Default: 0.3
    
    # Directories
    SKILLS_DIRECTORY          # Default: ./skills
    
    # Logging
    LOG_LEVEL                  # Default: INFO
```

### Authentication Methods

**Method 1: API Key (Recommended for Development)**
```env
AZURE_OPENAI_API_KEY=sk-...
```

**Method 2: Azure AD (Recommended for Production)**
```env
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
```

The system automatically selects the authentication method based on available credentials.

---

## 💻 Usage

### 1. **Basic Command Line Usage**

```python
from core.agent import SkillBasedAgent

# Initialize agent
agent = SkillBasedAgent()

# Process a simple query
response = agent.process_query("What is the capital of France?", use_skills=False)
print(response)
```

### 2. **Using Skills (Automatic Matching)**

```python
# Agent automatically matches relevant skills
response = agent.process_query(
    "Write a Python function to reverse a string",
    use_skills=True  # Enable skill matching
)
print(response)
```

### 3. **Script Execution**

```python
# If python_executor skill is matched, scripts run automatically
response = agent.process_query(
    "Run calculator.py to calculate 5 times 3"
)
# The agent detects the request, runs the script, and interprets results
```

### 4. **Streaming Responses**

```python
# Stream response as it's generated
for chunk in agent.process_query(
    "Explain neural networks",
    stream=True
):
    print(chunk, end="", flush=True)
```

### 5. **Force-Use Specific Skill**

```python
# Use a specific skill without matching
response = agent.use_specific_skill(
    "code-assistant",
    "Explain what this code does: def fib(n): return n if n<2 else fib(n-1)+fib(n-2)"
)
print(response)
```

### 6. **Multi-turn Conversation**

```python
# First message
agent.process_query("Write a Python function to sort a list")

# Follow-up (agent maintains context)
agent.process_query("Now optimize it for large lists")

# View conversation history
history = agent.get_conversation_history()
print(f"Messages: {len(history)}")
```

### 7. **Web UI (Streamlit)**

```bash
streamlit run streamlit_app.py
```

Access the interface at `http://localhost:8501`

**UI Features:**
- Real-time chat interface
- Skill selection and viewing
- Dataset upload (CSV/Excel)
- Response streaming
- Configuration display
- Clear history button

---

## 📁 Project Structure

```
skill-based-agent/
│
├── core/
│   ├── agent.py                 # Main agent orchestrator
│   ├── azure_client.py          # Azure OpenAI API wrapper
│   ├── skill_loader.py          # Skill discovery and loading
│   └── skill_matcher.py         # LLM-based skill matching
│
├── utils/
│   ├── logger.py                # Logging utilities
│   └── helpers.py               # Token counting, text processing
│
├── skills/
│   ├── code-assistant/
│   │   ├── SKILL.md             # Skill definition and instructions
│   │   ├── tools.py             # Custom tools (optional)
│   │   └── scripts/             # Executable scripts
│   │
│   ├── python_executor/
│   │   ├── SKILL.md
│   │   ├── tools.py             # Script execution engine
│   │   └── scripts/
│   │       ├── hello.py
│   │       ├── calculator.py
│   │       └── ...
│   │
│   └── [other-skills]/
│
├── config.py                    # Configuration management
├── example.py                   # Usage examples
├── check_output.py              # Testing script execution
├── test_executor.py             # Unit tests
├── streamlit_app.py             # Web UI
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

---

## 🧠 Core Components

### 1. SkillBasedAgent (`agent.py`)

**Main orchestrator class that:**
- Initializes all sub-components
- Manages conversation state
- Routes queries to skills
- Detects and executes scripts
- Generates responses

**Key Methods:**

```python
# Main query processing
process_query(user_query, use_skills=True, stream=False)
    → Processes query, matches skills, executes scripts

# Skill management
use_specific_skill(skill_name, user_query)
    → Force use of specific skill

get_available_skills()
    → Returns formatted skill summary

# Conversation management
clear_history()
    → Clears conversation history

reload_skills()
    → Reloads skills from disk

get_conversation_history()
    → Returns conversation history
```

### 2. AzureOpenAIClient (`azure_client.py`)

**Wrapper around Azure OpenAI API that:**
- Manages authentication (API key or Azure AD)
- Sends requests to Azure OpenAI
- Handles streaming responses
- Provides error handling

**Key Methods:**

```python
chat_completion(messages, temperature=None, max_tokens=None, stream=False)
    → Generate chat completion

get_response_text(response)
    → Extract text from response object

stream_response(stream)
    → Generator that yields streamed text chunks
```

### 3. SkillLoader (`skill_loader.py`)

**Discovers and loads skills from disk:**
- Scans `skills/` directory
- Reads `SKILL.md` files
- Extracts skill metadata
- Checks for custom tools

**Key Methods:**

```python
get_skill(skill_name)
    → Get specific skill

get_all_skills()
    → Get all loaded skills

get_skills_summary()
    → Get formatted skill list

reload_skills()
    → Reload skills from disk
```

### 4. SkillMatcher (`skill_matcher.py`)

**Matches queries to relevant skills using LLM:**
- Sends query to Azure OpenAI
- Ranks available skills by relevance
- Returns top 3 matches
- Fallback to first skill on error

**Key Methods:**

```python
match_skills(user_query, top_k=3)
    → Match query to relevant skills

force_match_skill(skill_name)
    → Get specific skill by name
```

---

## 🎯 Skills System

### What is a Skill?

A **skill** is a modular domain of expertise defined by:
1. **SKILL.md** - Instruction file with guidelines
2. **tools.py** (optional) - Custom Python functions
3. **scripts/** (optional) - Executable Python scripts

### Skill Structure

```
skills/code-assistant/
├── SKILL.md                 # Main instruction file
├── tools.py                 # Optional: Custom tools
└── scripts/
    ├── hello.py
    ├── calculator.py
    └── ...
```

### SKILL.md Format

Every skill must have a `SKILL.md` file with:

```markdown
# Metadata

**Name:** [Skill Name]
**Description:** [What the skill does]

---

# Instructions

## Guidelines
- Specific instructions for the skill domain
- Best practices and principles
- Common patterns and approaches

## When to Use
- Keywords that trigger this skill
- Example use cases

## Responsibilities
✅ What you SHOULD do
❌ What you should NOT do
```

### Example: Code Assistant Skill

```yaml
Name: Code Assistant
Description: Help with programming tasks, code review, debugging
Keywords: code, program, function, debug, error, implement

Instructions Include:
- Code Quality Principles
- Problem-Solving Approach
- Best Practices by Language
- When Writing Code
- Code Review Guidelines
```

### How Skills Are Used

```
User Query
    │
    ▼
[SkillMatcher]
    │
    ├─→ "Write a Python function"
    │    ▼
    │    [Skill: Code Assistant]
    │    [Score: 0.95]
    │
    └─→ [Add skill instructions to system prompt]
        │
        ▼
    [Azure OpenAI receives]
        - System prompt with skill instructions
        - User query
        - Conversation history
        │
        ▼
    [Response generated with skill context]
```

### Creating New Skills

1. Create skill directory:
```bash
mkdir skills/my-skill
```

2. Create `SKILL.md`:
```markdown
# Metadata
**Name:** My Skill
**Description:** What my skill does

---

# Instructions
[Your instructions here]
```

3. Optionally add `tools.py` for custom functions

4. Optionally add `scripts/` with Python scripts

5. Agent automatically discovers and loads the skill

---

## 🚀 Script Execution

### How Script Execution Works

```
User Query: "Run calculator.py to calculate 5 plus 3"
    │
    ▼
[SkillMatcher] → "python_executor" skill matched
    │
    ▼
[_check_for_script_execution()]
    │
    ├─→ Send to LLM: "Should I execute a script?"
    │
    ▼
[LLM Response] → "EXECUTE:calculator.py:add,5,3"
    │
    ▼
[_execute_python_script_tool()]
    │
    ├─→ Validate script exists
    ├─→ Parse arguments
    ├─→ Execute: python calculator.py add 5 3
    │
    ▼
[Capture Output]
    │
    ├─→ stdout: "Result: 8.0"
    ├─→ stderr: ""
    ├─→ exit_code: 0
    │
    ▼
[Format Result]
    │
    └─→ Include in system prompt for LLM
        │
        ▼
    [LLM Interprets] → "5 + 3 = 8"
        │
        ▼
    User sees: "5 + 3 = 8"
```

### Script Execution Format

**Detection Prompt Format:**
```
User Query: [user's query]
Available Scripts: [list of scripts]

Response Format:
EXECUTE:<script_name>:<arg1>,<arg2>,...
NO_EXECUTE
```

**Examples:**
- "run hello script" → `EXECUTE:hello.py:`
- "calculate 5 plus 3" → `EXECUTE:calculator.py:add,5,3`
- "what is 2+2" → `NO_EXECUTE`

### Script Tools (`tools.py`)

Provides safe script execution:

```python
def execute_python_script(script_name, args=None, timeout=10)
    """Execute a Python script from scripts/ directory"""

def format_execution_result(result)
    """Format script output for display"""

def list_available_scripts()
    """List all executable scripts"""

def get_script_info(script_name)
    """Get metadata about a script"""
```

---

## 🎨 Advanced Features

### 1. Token Management

```python
from utils.helpers import count_tokens, truncate_text

# Count tokens in a message
tokens = count_tokens("Hello, how are you?")

# Truncate text to fit token limit
truncated = truncate_text(long_text, max_tokens=2000)
```

### 2. Conversation History Management

```python
# Automatic history management
agent.conversation_history  # Last 10 messages kept

# Manual history control
history = agent.get_conversation_history()
agent.clear_history()
```

### 3. Streaming Responses

```python
# Real-time streaming
for chunk in agent.process_query(query, stream=True):
    print(chunk, end="", flush=True)
```

### 4. Flexible Skill Matching

```python
# Automatic matching
response = agent.process_query(query, use_skills=True)

# Without skills
response = agent.process_query(query, use_skills=False)

# Force specific skill
response = agent.use_specific_skill("code-assistant", query)
```

### 5. Dataset Integration

```python
# Streamlit UI supports CSV/Excel uploads
# Dataset context automatically added to queries
```

### 6. Logging and Debugging

```python
from utils.logger import logger

# Logs are written to stdout and optionally to file
logger.info("User started chat")
logger.debug("Processing query")
logger.error("Failed to match skill")
```

---

## 📚 Examples

### Example 1: Basic Query Without Skills

```python
from core.agent import SkillBasedAgent

agent = SkillBasedAgent()
response = agent.process_query(
    "What is the capital of France?",
    use_skills=False
)
print(response)
# Output: The capital of France is Paris. It is the most populous city in the country...
```

### Example 2: Code Writing with Skill Matching

```python
response = agent.process_query(
    "Write a Python function to calculate factorial",
    use_skills=True
)
# Agent matches "code-assistant" skill
# Skill instructions included in system prompt
# Response includes well-structured code with explanation
```

### Example 3: Script Execution

```python
response = agent.process_query(
    "Run the calculator to multiply 15 by 7"
)
# Agent detects "python_executor" skill
# Automatically runs: python calculator.py multiply 15 7
# Captures output: Result: 105.0
# Explains: "15 × 7 = 105"
```

### Example 4: Multi-turn Conversation

```python
# First turn
agent.process_query("Write a function to reverse a string")

# Second turn (context maintained)
agent.process_query("How would you optimize it for very long strings?")

# Agent remembers previous response and provides optimization
```

### Example 5: Streaming Response

```python
print("Agent: ", end="", flush=True)
for chunk in agent.process_query("Explain AI", stream=True):
    print(chunk, end="", flush=True)
print()

# Output streams in real-time
```

### Example 6: Interactive Mode

```bash
python example.py interactive
```

Provides a chat interface where you can:
- Chat with the agent naturally
- Type 'quit' to exit
- Type 'clear' to clear history
- Type 'skills' to list available skills

---

## 🧪 Testing

### Run Unit Tests

```bash
python test_executor.py
```

**Test Coverage:**
- List available scripts
- Get script information
- Execute hello.py
- Execute calculator with arguments
- Handle non-existent scripts

### Test Automatic Execution

```bash
python check_output.py
```

Tests:
- "Run the calculator.py script to calculate 11 multiplied by 7"
- "Run the abc.py script and give me the output"

### Manual Testing

```python
from core.agent import SkillBasedAgent

# Test 1: Skill matching
agent = SkillBasedAgent()
response = agent.process_query("Write code to read a CSV")
print("Test 1 - Skill matching: PASS")

# Test 2: Script execution
response = agent.process_query("Run hello.py")
print("Test 2 - Script execution: PASS")

# Test 3: Conversation context
agent.process_query("Write a function")
response = agent.process_query("Optimize it")
print("Test 3 - Context: PASS")
```

---

## 🎓 Interview Preparation

### Key Concepts to Understand

#### 1. **System Design**
- How components interact (Agent → Matcher → Client → LLM)
- Message flow and data transformation
- Error handling and fallback mechanisms
- Scalability considerations

#### 2. **Skill Matching Algorithm**
- LLM-based vs. similarity-based approaches
- Ranking and scoring mechanism
- Top-k selection (why 3?)
- Fallback strategies

#### 3. **Script Execution Pipeline**
- Safety considerations
- Argument parsing and validation
- Output capture (stdout/stderr)
- Timeout handling
- Result formatting

#### 4. **Conversation Management**
- Context window optimization (last 10 messages)
- Token counting and limits
- History persistence
- Memory considerations

#### 5. **Authentication**
- API Key vs. Azure AD
- Token management
- Credential security
- Multi-environment support

### Common Interview Questions

**Q1: How does the agent decide which skill to use?**
```
A: The SkillMatcher sends the user query + all available skills 
to Azure OpenAI with a specific prompt asking it to rank skills 
by relevance. The LLM returns skill numbers (1, 2, 3...), which 
are parsed and the top-k skills are selected.

Why LLM? Because it understands semantic meaning better than 
keyword matching. Trade-off: Slower than similarity search but 
more accurate for complex queries.
```

**Q2: How do you prevent scripts from running malicious code?**
```
A: Current approach:
1. Scripts must be in the predefined skills/*/scripts/ directory
2. Scripts are validated before execution
3. Timeout is enforced (10-30 seconds)
4. stdout/stderr captured safely
5. Exit codes checked

For production:
- Sandboxing (Docker, subprocess isolation)
- Code signing
- Admin approval for new scripts
- Audit logging of all executions
```

**Q3: Why limit conversation history to last 10 messages?**
```
A: Token budget management. With Max_tokens=4000 and including:
- System prompt (with all skill instructions)
- Conversation history
- New user message

Including too much history = fewer tokens for response generation.
Last 10 messages = good balance between context and generation.

Optimization: Implement summarization for older messages.
```

**Q4: What happens if skill matching fails?**
```
A: Fallback strategy:
1. Try LLM-based matching → Parse response
2. If parsing fails → Return first skill
3. If no skills → Process without skills (direct LLM)

Always graceful degradation, never return error.
```

**Q5: How does automatic script execution work?**
```
A: Two-stage process:
1. Skill Matching: If "python_executor" skill matched
2. Script Detection: Send query to LLM asking:
   "Should I execute a script? If yes, which one?"
   LLM responds: "EXECUTE:script_name:arg1,arg2" or "NO_EXECUTE"

This prevents executing scripts for "theoretical" questions.
Example:
- "What would happen if I ran..." → NO_EXECUTE
- "Run calculator..." → EXECUTE:calculator.py:...
```

**Q6: How do you handle token limits?**
```
A: 1. Counting: tiktoken for accurate token counts
2. Limiting: Last N messages in history
3. Truncation: Truncate long messages to fit
4. Configuration: MAX_TOKENS is configurable
5. Monitoring: Log total tokens before API call

Could improve with:
- Message summarization
- Compression algorithms
- Adaptive history window
```

**Q7: What are the main architectural decisions?**
```
A: 1. LLM-based skill matching (vs. similarity search)
   → Better for semantic understanding
   
2. Automatic script execution (vs. user-triggered)
   → More seamless UX, requires careful detection
   
3. Skill instructions in system prompt (vs. RAG)
   → Simpler, ensures consistency, costs tokens
   
4. Streaming responses
   → Better UX, but complex to manage
   
5. Azure OpenAI (vs. other LLMs)
   → Enterprise integration, compliance
```

**Q8: How would you scale this to handle 1000s of users?**
```
A: 1. API Layer: FastAPI with async endpoints
2. Queue: Celery/Redis for async job processing
3. Caching: Redis for skill definitions, conversation summaries
4. Database: PostgreSQL for conversation persistence
5. Load Balancing: Kubernetes for horizontal scaling
6. Monitoring: Prometheus/Grafana for metrics
7. Rate Limiting: Per-user token quotas
8. Cost Optimization: Batch processing, cheaper models for simple queries

Current system is single-user/session-based.
```

**Q9: What are the limitations of the current approach?**
```
A: 1. Context Window: Fixed 10-message history
2. Skill Instructions in Prompt: Increases token cost
3. LLM-based Matching: Slower than similarity search
4. No Persistence: Conversations lost on restart
5. Single Model: Can't switch between models per query
6. Error Handling: Limited retry logic
7. Security: No sandboxing for scripts
8. Scalability: Single-threaded, session-based

Improvements in interview:
"I would implement X to address Y limitation..."
```

**Q10: How do you test this system?**
```
A: 1. Unit Tests: Test individual components
2. Integration Tests: Test skill matching + execution
3. E2E Tests: Full query → response pipeline
4. Mock Tests: Mock Azure OpenAI for development
5. Load Tests: Test with concurrent users
6. Performance Tests: Measure latency, tokens used

Current system: Basic pytest files, manual testing via CLI/Streamlit
```

### Talking Points for Interview

1. **"I built a system inspired by Claude's skill architecture..."**
   - Demonstrates knowledge of current AI trends
   - Shows ability to learn from examples

2. **"The key innovation is automatic script execution detection..."**
   - Highlights problem-solving
   - Shows deep understanding of system design

3. **"I chose LLM-based skill matching over keyword matching because..."**
   - Demonstrates trade-off thinking
   - Shows reasoning about design decisions

4. **"The system handles errors gracefully with fallback strategies..."**
   - Shows production-ready thinking
   - Demonstrates robustness considerations

5. **"I would scale this by implementing..."**
   - Shows forward-thinking
   - Demonstrates system design knowledge

---

## 🔧 Troubleshooting

### Issue: "No module named 'openai'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Azure OpenAI API key not found"

**Solution:**
```bash
# Create .env file with proper credentials
echo "AZURE_OPENAI_API_KEY=your-key" > .env
```

### Issue: "Skills not loading"

**Solution:**
```bash
# Check skills directory exists
ls skills/
# Ensure each skill has SKILL.md
ls skills/*/SKILL.md
```

### Issue: "Script execution timeout"

**Solution:**
```python
# Increase timeout in agent.py
result = self.execute_script(script_name, args=args or [], timeout=60)
```

### Issue: "Token limit exceeded"

**Solution:**
```python
# Reduce max messages in history
max_history_messages = 5  # was 10
```

---

## 📝 Environment Variables Reference

```env
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Authentication (choose one)
AZURE_OPENAI_API_KEY=your-key
# OR
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...

# Recommended
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional
MAX_TOKENS=4000
TEMPERATURE=0.3
SKILLS_DIRECTORY=./skills
LOG_LEVEL=INFO
```

---

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Python-OpenAI SDK](https://github.com/openai/openai-python)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Claude Skills Documentation](https://docs.claude.com/)

---

## 📄 License

This project is provided as-is for educational and interview preparation purposes.

---

## ✨ Key Takeaways

1. **Modular Architecture**: Skills, clients, and loaders are decoupled
2. **LLM-Centric Design**: LLM used not just for output but also for decision-making
3. **Graceful Degradation**: System always provides response, never fails silently
4. **Production Considerations**: Error handling, logging, configuration management
5. **Extensibility**: Easy to add new skills, new script types, new integrations

---

**Last Updated**: 2026  
**Interview Focus**: System design, LLM integration, Python architecture
