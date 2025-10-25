# ⚡ Agentverse Quick Start - 5 Minutes

Get your agents on Agentverse in 5 minutes with mailbox agents.

---

## 🎯 What Are Mailbox Agents?

Mailbox agents run **locally** but get **public Agentverse addresses**.

**Perfect for hackathons:**
- ✅ Agents run on your laptop (fast, full control)
- ✅ Get public addresses (accessible from internet)
- ✅ No code upload needed
- ✅ Heavy ML (Conway) stays local

---

## 🚀 Setup (5 Steps)

### **Step 1: Create Agentverse Account** (1 min)

```bash
# Open browser
https://agentverse.ai

# Sign up with GitHub, Google, or email
```

### **Step 2: Create Mailboxes** (2 min)

In Agentverse UI:
1. Click **"Mailboxes"** in sidebar
2. Click **"Create Mailbox"**
3. Name: `coordinator_mailbox`
4. Copy the mailbox key (looks like: `0a1b2c3...`)
5. Repeat for all 7 agents

**Agent names:**
- coordinator_mailbox
- eligibility_mailbox
- pattern_mailbox
- discovery_mailbox
- matching_mailbox
- site_mailbox
- prediction_mailbox

### **Step 3: Run Setup Script** (1 min)

```bash
cd backend
python setup_agentverse.py
```

Follow prompts and paste your 7 mailbox keys.

**Output:** Creates `.env.agentverse` file with your keys.

### **Step 4: Load Environment** (10 sec)

```bash
# Linux/Mac
source .env.agentverse

# Or
set -a; source .env.agentverse; set +a

# Windows (PowerShell)
Get-Content .env.agentverse | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Item -Path "env:$name" -Value $value
}
```

### **Step 5: Run Agents** (10 sec)

```bash
python run_agents_mailbox.py
```

**Done!** Your agents now have public Agentverse addresses! 🎉

---

## 🧪 Test It Works

### **Check Agent Addresses**

Look for these in startup logs:
```
✓ Added coordinator agent: agent1q2w3e4r5t6y7u8i9o0...
✓ Added eligibility agent: agent1q9o8i7u6y5t4r3e2w1...
```

These are your **public Agentverse addresses**!

### **Test Communication**

```python
# test_public_agent.py
from uagents import Agent, Context
from agents.models import UserQuery

test_agent = Agent(name="test", seed="test123")

# Use your coordinator's public address
COORDINATOR_ADDRESS = "agent1q..."  # From logs

@test_agent.on_interval(period=10.0)
async def send_query(ctx: Context):
    ctx.logger.info("Sending query to public agent...")

    response = await ctx.send(
        COORDINATOR_ADDRESS,
        UserQuery(
            trial_id="NCT00100000",
            query="Test from external agent",
            filters={}
        ),
        timeout=30.0
    )

    ctx.logger.info(f"Response: {response}")

if __name__ == "__main__":
    test_agent.run()
```

Run:
```bash
python test_public_agent.py
```

If you see a response, **it works!** Your agents are publicly accessible.

---

## 📋 What You Get

### **Before (Local Only):**
```
Your Laptop
    └─ 7 Agents
       • Only accessible on localhost
       • Not reachable from internet
```

### **After (Mailbox Agents):**
```
Internet
    ↓
Agentverse Mailbox (public addresses)
    ↓
Your Laptop
    └─ 7 Agents (local execution)
       • Publicly accessible via Agentverse
       • Fast local processing
       • Public addresses for discovery
```

---

## 🎨 For Your Demo

### **Show This:**

1. **Agents on Agentverse:**
   - Show Agentverse dashboard with your mailboxes
   - "Our agents are on Fetch.ai's decentralized network"

2. **Public Addresses:**
   - Show agent addresses in logs
   - "Each agent has a globally unique address"

3. **Cross-Network Communication:**
   - Run test agent from different machine
   - "Agents can communicate across the internet"

### **Say This:**

> "We've deployed our multi-agent system to **Fetch.ai's Agentverse**, a decentralized agent network. Each of our 7 agents has a public address, meaning they could coordinate clinical trial matching across hospitals worldwide. The Coordinator orchestrates everything through autonomous message passing - no centralized server required."

---

## 🔍 Monitoring

### **In Agentverse Dashboard:**

Go to https://agentverse.ai → Mailboxes

You'll see:
- 📬 Message queue status
- 📊 Messages sent/received
- 🟢 Connection status
- 📝 Recent activity

### **In Your Logs:**

```bash
# Your local agent logs
tail -f logs/agents.log

# Look for:
INFO - Message received via Agentverse
INFO - Sending response via mailbox
```

---

## ⚙️ Configuration

### **Environment Variables:**

```bash
# .env.agentverse (created by setup script)
COORDINATOR_MAILBOX=0a1b2c3...
ELIGIBILITY_MAILBOX=4d5e6f7...
PATTERN_MAILBOX=8g9h0i1...
DISCOVERY_MAILBOX=2j3k4l5...
MATCHING_MAILBOX=6m7n8o9...
SITE_MAILBOX=0p1q2r3...
PREDICTION_MAILBOX=4s5t6u7...

USE_AGENTVERSE_MAILBOXES=true
```

### **Agent Code (Automatic):**

The setup script modifies agents to use mailboxes:

```python
# Before
agent = Agent(
    name="coordinator",
    seed="...",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# After (with mailbox)
agent = Agent(
    name="coordinator",
    seed="...",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    mailbox="0a1b2c3...@https://agentverse.ai"  # Public address!
)
```

---

## 🐛 Troubleshooting

### **Issue: "No mailbox key found"**

```
WARNING - No mailbox key for COORDINATOR_MAILBOX - using local only
```

**Fix:**
```bash
# Make sure you loaded environment
source .env.agentverse

# Check it's set
echo $COORDINATOR_MAILBOX
```

### **Issue: "Connection to Agentverse failed"**

**Check:**
1. Internet connection working?
2. Agentverse.ai accessible? (try in browser)
3. Mailbox key correct? (check for typos)

**Test connection:**
```bash
curl https://agentverse.ai
# Should return HTML
```

### **Issue: "Messages not being delivered"**

**Possible causes:**
1. Mailbox key incorrect
2. Agent not registered properly
3. Network firewall blocking

**Debug:**
```python
# Add verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 💡 Pro Tips

### **Tip 1: Keep Mailbox Keys Secret**

```bash
# Never commit .env.agentverse
echo ".env.agentverse" >> .gitignore

# Share keys securely with team
# Use 1Password, LastPass, or encrypted messaging
```

### **Tip 2: Test Locally First**

```bash
# Run without mailboxes first
python run_agents.py

# Once working, add mailboxes
source .env.agentverse
python run_agents_mailbox.py
```

### **Tip 3: Have Local Fallback**

During demo, if internet fails:
```bash
# Run local-only version
python run_agents.py
```

### **Tip 4: Monitor in Real-Time**

Open two terminals:
```bash
# Terminal 1: Run agents
python run_agents_mailbox.py

# Terminal 2: Watch logs
tail -f logs/agents.log | grep -i "agentverse\|mailbox"
```

---

## 📊 Comparison: Deployment Options

| Feature | Local Only | Mailbox Agents | Hosted Agents |
|---------|-----------|----------------|---------------|
| Setup Time | 0 min | 5 min | 15-30 min |
| Execution | Local | Local | Cloud |
| Public Address | ❌ No | ✅ Yes | ✅ Yes |
| Internet Needed | ❌ No | ✅ Yes | ✅ Yes |
| Heavy ML (Conway) | ✅ Fast | ✅ Fast | ⚠️ Limited |
| Demo Reliability | ✅ High | ⚠️ Medium | ⚠️ Medium |
| **Recommended For** | Development | **Hackathon** | Production |

**Verdict:** Use **Mailbox Agents** for hackathons!

---

## 🎯 Quick Commands

```bash
# Setup
python setup_agentverse.py

# Load environment
source .env.agentverse

# Run agents with mailboxes
python run_agents_mailbox.py

# Run tests
python test_agents.py

# Check environment
env | grep MAILBOX

# Kill agents
pkill -f "python run_agents"
```

---

## ✅ Success Checklist

- [ ] Agentverse account created
- [ ] 7 mailboxes created
- [ ] Mailbox keys saved in `.env.agentverse`
- [ ] Environment loaded (`source .env.agentverse`)
- [ ] Agents running (`python run_agents_mailbox.py`)
- [ ] Public addresses visible in logs
- [ ] Test communication working
- [ ] Ready to demo!

---

## 🚀 You're Ready!

Your agents are now:
- ✅ Running on your laptop (fast & reliable)
- ✅ Accessible via public Agentverse addresses
- ✅ Discoverable on Fetch.ai's network
- ✅ Ready to impress judges!

**Time to demo your decentralized multi-agent system! 🎉**

---

## 📚 More Info

- **Full Guide:** `AGENTVERSE_DEPLOYMENT.md`
- **Agent Docs:** `AGENTS_README.md`
- **Quick Start:** `QUICKSTART_AGENTS.md`
- **Fetch.ai Docs:** https://docs.fetch.ai

---

**Questions? Check the full deployment guide or Fetch.ai Discord!**
