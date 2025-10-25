# 🚀 Deploying Agents to Agentverse

Complete guide to deploying your TrialMatch AI agents to Fetch.ai's Agentverse cloud platform.

---

## 🌐 What is Agentverse?

**Agentverse** is Fetch.ai's cloud hosting platform for agents. Benefits:

- ✅ **Public Addresses** - Your agents get permanent, publicly accessible addresses
- ✅ **Always Online** - No need to keep your laptop running
- ✅ **Scalable** - Fetch.ai handles infrastructure
- ✅ **Discoverable** - Other agents can find yours via Almanac
- ✅ **Free Tier** - No cost for basic usage

**Agentverse URL:** https://agentverse.ai

---

## 📋 Prerequisites

### **1. Create Agentverse Account**

1. Go to https://agentverse.ai
2. Click "Sign Up" or "Login"
3. Create account (can use GitHub, Google, or email)
4. Verify email

### **2. Get API Key**

1. Login to Agentverse
2. Go to **Profile** → **API Keys**
3. Click **"Create New API Key"**
4. Copy and save your API key securely

---

## 🏗️ Deployment Options

### **Option 1: Agentverse Hosted Agents** (Recommended)
Upload agent code to Agentverse - they run it for you

### **Option 2: Mailbox Agents**
Run agents locally but get public Agentverse addresses

### **Option 3: ASI-1 Alliance Chain**
Deploy to blockchain for maximum decentralization (advanced)

---

## 🚀 Option 1: Deploy to Agentverse (Hosted)

### **Step 1: Prepare Agent for Deployment**

Agentverse agents need slight modifications. Create deployment versions:

```python
# agents/coordinator_agent_agentverse.py
from uagents import Agent, Context, Bureau
from agents.models import UserQuery, CoordinatorResponse
import os

# Get Agentverse configuration
AGENT_MAILBOX_KEY = os.getenv("AGENT_MAILBOX_KEY")

# Create agent with Agentverse configuration
agent = Agent(
    name="trial_coordinator",
    seed="coordinator_trial_match_seed_2024",
    # No port/endpoint needed for Agentverse!
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai" if AGENT_MAILBOX_KEY else None
)

# ... rest of your agent code (handlers, etc.)

if __name__ == "__main__":
    agent.run()
```

**Key Changes for Agentverse:**
- ❌ Remove `port` parameter
- ❌ Remove `endpoint` parameter
- ✅ Add `mailbox` parameter with your Agentverse key

### **Step 2: Create Agentverse Agent**

#### **Via Web UI:**

1. **Login to Agentverse:** https://agentverse.ai
2. **Click "Create Agent"**
3. **Fill in details:**
   - **Name:** `trial_coordinator`
   - **Description:** "Orchestrates trial matching workflow"
   - **Type:** Select "Hosted Agent"

4. **Upload Code:**
   - Click "Code" tab
   - Paste your agent code (modified version above)
   - Or upload file

5. **Set Environment Variables:**
   - Add any required env vars (API keys, etc.)

6. **Deploy:**
   - Click "Deploy"
   - Wait for agent to start (30-60 seconds)
   - Copy the agent address shown

#### **Via CLI (Alternative):**

```bash
# Install Agentverse CLI
pip install agentverse

# Login
agentverse login

# Deploy agent
agentverse deploy agents/coordinator_agent_agentverse.py \
  --name "trial_coordinator" \
  --description "Trial matching coordinator"
```

### **Step 3: Configure Agent Dependencies**

In Agentverse UI, go to **Dependencies** tab and add:

```
uagents==0.11.0
pydantic==1.10.9
numpy>=1.24.0
```

**Note:** Keep dependencies minimal for Agentverse. Complex dependencies (sentence-transformers, sklearn) should run locally.

### **Step 4: Test Your Deployed Agent**

```python
# test_agentverse_agent.py
from uagents import Agent, Context
from agents.models import UserQuery, CoordinatorResponse

# Your local test agent
test_agent = Agent(name="test_client", seed="test_seed_123")

# Address of your deployed Agentverse agent
DEPLOYED_COORDINATOR = "agent1q..." # Copy from Agentverse UI

@test_agent.on_interval(period=10.0)
async def send_query(ctx: Context):
    ctx.logger.info("Sending query to Agentverse coordinator...")

    response = await ctx.send(
        DEPLOYED_COORDINATOR,
        UserQuery(
            trial_id="NCT00100000",
            query="Test query from local agent",
            filters={}
        ),
        timeout=30.0
    )

    if response:
        ctx.logger.info(f"Got response: {response}")
    else:
        ctx.logger.error("No response from Agentverse agent")

if __name__ == "__main__":
    test_agent.run()
```

---

## 📮 Option 2: Mailbox Agents (Hybrid)

**Best for:** Running complex agents locally while having public addresses.

### **How Mailbox Works:**

```
Internet
    ↓
Agentverse Mailbox (public address)
    ↓
Your Local Agent (private network)
```

Your agent runs locally but gets a public Agentverse address for communication.

### **Setup:**

1. **Get Mailbox Key from Agentverse:**
   - Go to https://agentverse.ai
   - Navigate to **Mailboxes**
   - Click **"Create Mailbox"**
   - Copy the mailbox key

2. **Configure Local Agent:**

```python
# agents/coordinator_agent_mailbox.py
import os
from uagents import Agent, Context

# Get mailbox key from environment
MAILBOX_KEY = os.getenv("AGENTVERSE_MAILBOX_KEY")

agent = Agent(
    name="trial_coordinator",
    seed="coordinator_trial_match_seed_2024",
    mailbox=f"{MAILBOX_KEY}@https://agentverse.ai",
    # Still need port for local HTTP endpoint
    port=8000,
    endpoint=[f"http://localhost:8000/submit"]
)

# ... rest of agent code
```

3. **Set Environment Variable:**

```bash
export AGENTVERSE_MAILBOX_KEY="your_mailbox_key_here"
python agents/coordinator_agent_mailbox.py
```

4. **Your Agent Now Has Public Address:**
   - Local: Still accessible at `localhost:8000`
   - Public: Accessible via Agentverse mailbox address
   - Other agents can send messages to your public address

---

## ⛓️ Option 3: ASI-1 Alliance Chain (Advanced)

**ASI-1** is the Alliance Chain connecting Fetch.ai, Ocean Protocol, and SingularityNET.

### **When to Use:**
- Need maximum decentralization
- Want blockchain-level security
- Building production dApps
- Need token integration

### **Deployment Steps:**

1. **Get Test Tokens:**
   ```bash
   # Connect to testnet
   fetchd config chain-id agentverse-1
   fetchd config node https://rpc-agentverse.fetch.ai:443

   # Request test tokens from faucet
   # Visit: https://faucet.agentverse.ai
   ```

2. **Deploy Agent to Chain:**
   ```python
   from uagents import Agent

   agent = Agent(
       name="trial_coordinator",
       seed="coordinator_seed",
       # Connect to Alliance Chain
       almanac_contract="fetch1...",  # Contract address
       ledger_url="https://rpc-agentverse.fetch.ai:443"
   )
   ```

3. **Register on Almanac:**
   ```python
   # Agent automatically registers on startup
   # Other agents can discover via Almanac queries
   ```

---

## 🎯 Recommended Deployment Strategy for TrialMatch AI

### **For CalHacks Demo:**

**Use Mailbox Agents** (Option 2) for best of both worlds:

```
┌─────────────────────────────────────────────────────────┐
│  AGENTVERSE (Public Addresses)                          │
│  - Coordinator Mailbox                                  │
│  - Gives agent public address                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────���──────────────────────────┐
│  YOUR LAPTOP (Local Execution)                          │
│  - All 7 agents run locally                             │
│  - Conway engine runs locally (heavy ML)                │
│  - Fast processing, full control                        │
│  - But accessible via public addresses                  │
└─────────────────────────────────────────────────────────┘
```

### **Why This Works:**

✅ **Public Access** - Judges can interact with agents remotely
✅ **Fast Execution** - Conway ML runs on your hardware
✅ **Full Control** - Easy debugging during demo
✅ **Impressive** - "Our agents are on Fetch.ai's network!"

---

## 📝 Quick Deployment Guide for Your 7 Agents

### **Step 1: Create Deployment Script**

```python
# deploy_to_agentverse.py
import os
from uagents import Agent

# Get mailbox keys from Agentverse
MAILBOXES = {
    "coordinator": os.getenv("COORDINATOR_MAILBOX"),
    "eligibility": os.getenv("ELIGIBILITY_MAILBOX"),
    "pattern": os.getenv("PATTERN_MAILBOX"),
    "discovery": os.getenv("DISCOVERY_MAILBOX"),
    "matching": os.getenv("MATCHING_MAILBOX"),
    "site": os.getenv("SITE_MAILBOX"),
    "prediction": os.getenv("PREDICTION_MAILBOX"),
}

def create_mailbox_agent(agent_name, config):
    """Create agent with Agentverse mailbox"""
    mailbox_key = MAILBOXES.get(agent_name)

    if not mailbox_key:
        raise ValueError(f"No mailbox key for {agent_name}")

    return Agent(
        name=config["name"],
        seed=config["seed"],
        port=config["port"],
        endpoint=config["endpoint"],
        mailbox=f"{mailbox_key}@https://agentverse.ai"
    )

# Use this in your agents
```

### **Step 2: Get 7 Mailbox Keys**

1. Go to https://agentverse.ai
2. Create 7 mailboxes (one per agent):
   - `trial_coordinator_mailbox`
   - `eligibility_agent_mailbox`
   - `pattern_agent_mailbox`
   - `discovery_agent_mailbox`
   - `matching_agent_mailbox`
   - `site_agent_mailbox`
   - `prediction_agent_mailbox`

3. Copy each mailbox key

### **Step 3: Set Environment Variables**

```bash
# .env file
COORDINATOR_MAILBOX="your_coordinator_mailbox_key"
ELIGIBILITY_MAILBOX="your_eligibility_mailbox_key"
PATTERN_MAILBOX="your_pattern_mailbox_key"
DISCOVERY_MAILBOX="your_discovery_mailbox_key"
MATCHING_MAILBOX="your_matching_mailbox_key"
SITE_MAILBOX="your_site_mailbox_key"
PREDICTION_MAILBOX="your_prediction_mailbox_key"
```

```bash
# Load environment
source .env  # Linux/Mac
# OR
set -a; source .env; set +a  # Alternative
```

### **Step 4: Update Agent Config**

```python
# agents/config.py - Add mailbox support

class AgentConfig:
    @classmethod
    def get_agent_config(cls, agent_name: str, use_mailbox: bool = False) -> Dict:
        """Get configuration with optional mailbox"""
        config = cls._get_base_config(agent_name)

        if use_mailbox:
            mailbox_key = os.getenv(f"{agent_name.upper()}_MAILBOX")
            if mailbox_key:
                config["mailbox"] = f"{mailbox_key}@https://agentverse.ai"

        return config
```

### **Step 5: Run with Mailboxes**

```python
# run_agents_agentverse.py
from uagents import Bureau
import os

# Set mailbox mode
os.environ["USE_AGENTVERSE_MAILBOXES"] = "true"

# Import agents (they'll use mailbox config)
from agents.coordinator_agent import agent as coordinator
from agents.eligibility_agent import agent as eligibility
# ... etc

bureau = Bureau()
bureau.add(coordinator)
bureau.add(eligibility)
# ... add all agents

bureau.run()
```

---

## 🔍 Monitoring Deployed Agents

### **In Agentverse Dashboard:**

1. **Agent Status:**
   - Green = Running
   - Red = Stopped/Error
   - Yellow = Starting

2. **Logs:**
   - View real-time logs
   - Filter by level (INFO, ERROR, etc.)
   - Download logs

3. **Messages:**
   - See incoming/outgoing messages
   - Monitor message queue
   - Debug communication issues

4. **Metrics:**
   - Requests processed
   - Response times
   - Error rates

### **Programmatic Monitoring:**

```python
from uagents import Agent, Context
from agents.models import AgentStatus

monitor_agent = Agent(name="monitor", seed="monitor_seed")

AGENT_ADDRESSES = [
    "agent1q...",  # coordinator
    "agent1q...",  # eligibility
    # ... etc
]

@monitor_agent.on_interval(period=60.0)
async def check_agents(ctx: Context):
    """Check all agent statuses every minute"""
    for addr in AGENT_ADDRESSES:
        try:
            status = await ctx.send(
                addr,
                AgentStatus(agent_name="", status="", address="", uptime=0, requests_processed=0),
                timeout=5.0
            )

            if status:
                ctx.logger.info(f"✓ {status.agent_name}: {status.status}")
            else:
                ctx.logger.warning(f"✗ No response from {addr}")

        except Exception as e:
            ctx.logger.error(f"✗ Error checking {addr}: {e}")

if __name__ == "__main__":
    monitor_agent.run()
```

---

## 💡 Best Practices

### **Security**

1. **Never commit API keys**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Use environment variables**
   ```python
   import os
   MAILBOX_KEY = os.getenv("MAILBOX_KEY")
   ```

3. **Validate incoming messages**
   ```python
   @agent.on_query(model=UserQuery)
   async def handle_query(ctx: Context, sender: str, msg: UserQuery):
       # Validate sender
       if not is_authorized(sender):
           ctx.logger.warning(f"Unauthorized query from {sender}")
           return
       # ... process query
   ```

### **Performance**

1. **Keep heavy processing local**
   - Run ML models (Conway) locally
   - Use Agentverse for coordination only

2. **Use caching**
   ```python
   @agent.on_query(model=Request)
   async def handle_request(ctx: Context, sender: str, msg: Request):
       # Check cache first
       cached = ctx.storage.get(msg.id)
       if cached:
           return cached

       # Process and cache
       result = process(msg)
       ctx.storage.set(msg.id, result)
       return result
   ```

3. **Implement timeouts**
   ```python
   response = await ctx.send(addr, msg, timeout=30.0)
   ```

### **Reliability**

1. **Error handling**
   ```python
   try:
       response = await ctx.send(addr, msg, timeout=30.0)
   except TimeoutError:
       ctx.logger.error("Agent timeout - using fallback")
       response = fallback_response()
   except Exception as e:
       ctx.logger.error(f"Error: {e}")
       response = error_response()
   ```

2. **Retry logic**
   ```python
   for attempt in range(3):
       try:
           response = await ctx.send(addr, msg)
           break
       except Exception as e:
           if attempt == 2:
               raise
           await asyncio.sleep(2 ** attempt)  # Exponential backoff
   ```

---

## 🎓 Resources

### **Official Docs**
- **Agentverse:** https://docs.fetch.ai/guides/agentverse/
- **uagents:** https://docs.fetch.ai/guides/agents/
- **Mailbox:** https://docs.fetch.ai/guides/agents/mailbox

### **Community**
- **Discord:** https://discord.gg/fetchai
- **Telegram:** https://t.me/fetch_ai
- **GitHub:** https://github.com/fetchai/uAgents

### **Tutorials**
- Creating your first agent: https://docs.fetch.ai/guides/agents/quickstart
- Deploying to Agentverse: https://docs.fetch.ai/guides/agentverse/creating-agentverse-agents
- Mailbox setup: https://docs.fetch.ai/guides/agents/mailbox

---

## 🚀 Quick Commands Reference

```bash
# Install CLI
pip install agentverse

# Login
agentverse login

# List agents
agentverse list

# Deploy agent
agentverse deploy agent.py --name "my_agent"

# View logs
agentverse logs my_agent

# Stop agent
agentverse stop my_agent

# Delete agent
agentverse delete my_agent
```

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Agents work locally
- [ ] Dependencies minimal (for hosted agents)
- [ ] Environment variables configured
- [ ] Mailbox keys obtained (for mailbox agents)
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Security validated (no hardcoded keys)
- [ ] Monitoring setup
- [ ] Backup plan for demo (local fallback)

---

## 🎯 For Your CalHacks Demo

### **Recommended Approach:**

**Week Before:**
1. Get mailbox keys for all 7 agents
2. Test mailbox agents locally
3. Verify public addresses work

**Day Before:**
1. Deploy Coordinator to Agentverse (hosted)
2. Keep other 6 agents as mailbox agents (local)
3. Test end-to-end with public address

**Demo Day:**
1. Run all agents locally (fast, reliable)
2. Mention Agentverse integration in presentation
3. Show public addresses if internet allows
4. Have local-only version as backup

### **Demo Script:**

"Our agents don't just run locally - they're deployed on **Fetch.ai's Agentverse**, a decentralized agent network. Each agent has a public address accessible globally. This means our system could coordinate clinical trial matching across hospitals worldwide, all communicating through autonomous AI agents."

---

**You're now ready to deploy to Agentverse! 🚀**

Choose your deployment strategy and start with mailbox agents for maximum flexibility during your hackathon.
