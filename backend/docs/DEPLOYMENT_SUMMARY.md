# 🎯 Agentverse Deployment - Visual Summary

## 📊 Three Deployment Options

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  OPTION 1: LOCAL ONLY (Development)                               │
│  ────────────────────────────────                                 │
│                                                                    │
│  Your Laptop                                                       │
│  ├─ Coordinator Agent (localhost:8000)                            │
│  ├─ Eligibility Agent (localhost:8001)                            │
│  ├─ Pattern Agent (localhost:8002)                                │
│  ├─ Discovery Agent (localhost:8003)                              │
│  ├─ Matching Agent (localhost:8004)                               │
│  ├─ Site Agent (localhost:8005)                                   │
│  └─ Prediction Agent (localhost:8006)                             │
│                                                                    │
│  ✓ Fast & reliable                                                │
│  ✗ Not publicly accessible                                        │
│  ⏱ Setup: 0 minutes                                                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  OPTION 2: MAILBOX AGENTS (Recommended for Hackathons) ⭐         │
│  ──────────────────────────────────────────────────────           │
│                                                                    │
│  Internet                                                          │
│      ↓                                                             │
│  Agentverse Cloud                                                  │
│  ├─ coordinator_mailbox → agent1q2w3e4r5... (public address)      │
│  ├─ eligibility_mailbox → agent1q9o8i7u6... (public address)      │
│  ├─ pattern_mailbox → agent1q5t4r3e2w... (public address)         │
│  ├─ discovery_mailbox → agent1q1q2w3e4r... (public address)       │
│  ├─ matching_mailbox → agent1q7u8i9o0p... (public address)        │
│  ├─ site_mailbox → agent1q3e2w1q0p9o... (public address)          │
│  └─ prediction_mailbox → agent1q8i7u6y5t... (public address)      │
│      ↓                                                             │
│  Your Laptop (Local Execution)                                     │
│  ├─ Coordinator Agent (fast local processing)                     │
│  ├─ Eligibility Agent (fast local processing)                     │
│  ├─ Pattern Agent (fast local processing)                         │
│  ├─ Discovery Agent (fast local processing)                       │
│  ├─ Matching Agent (fast local processing)                        │
│  ├─ Site Agent (fast local processing)                            │
│  └─ Prediction Agent (fast local processing)                      │
│                                                                    │
│  ✓ Publicly accessible                                            │
│  ✓ Fast local execution                                           │
│  ✓ Conway ML runs locally                                         │
│  ✓ Can access from anywhere                                       │
│  ⏱ Setup: 5 minutes                                                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  OPTION 3: HOSTED AGENTS (Production)                             │
│  ─────────────────────────────────────                            │
│                                                                    │
│  Agentverse Cloud (Fetch.ai Infrastructure)                       │
│  ├─ Coordinator Agent (runs in cloud)                             │
│  ├─ Eligibility Agent (runs in cloud)                             │
│  ├─ Pattern Agent (runs in cloud)                                 │
│  ├─ Discovery Agent (runs in cloud)                               │
│  ├─ Matching Agent (runs in cloud)                                │
│  ├─ Site Agent (runs in cloud)                                    │
│  └─ Prediction Agent (runs in cloud)                              │
│                                                                    │
│  ✓ Always online                                                  │
│  ✓ Managed infrastructure                                         │
│  ✗ Limited compute (no heavy ML)                                  │
│  ✗ More complex setup                                             │
│  ⏱ Setup: 15-30 minutes                                            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recommendation: Use Mailbox Agents

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  FOR CALHACKS: USE MAILBOX AGENTS (OPTION 2)                      ║
║                                                                   ║
║  Why?                                                             ║
║  ✓ Best of both worlds                                            ║
║  ✓ Public addresses (impressive for demo)                         ║
║  ✓ Fast execution (runs on your hardware)                         ║
║  ✓ Conway ML works (no cloud compute limits)                      ║
║  ✓ Quick setup (5 minutes)                                        ║
║  ✓ Reliable (local fallback if internet fails)                    ║
║                                                                   ║
╚════════════════════���══════════════════════════════════════════════╝
```

---

## 🚀 Setup Flow for Mailbox Agents

```
Step 1: Create Account
┌──────────────────┐
│ agentverse.ai    │
│ Sign up          │
└────────┬─────────┘
         ↓

Step 2: Create Mailboxes
┌──────────────────┐
│ Create 7 mailboxes│
│ Copy keys        │
└────────┬─────────┘
         ↓

Step 3: Run Setup
┌──────────────────┐
│ python setup_    │
│ agentverse.py    │
└────────┬─────────┘
         ↓

Step 4: Load Environment
┌──────────────────┐
│ source .env.     │
│ agentverse       │
└────────┬─────────┘
         ↓

Step 5: Run Agents
┌──────────────────┐
│ python run_agents│
│ _mailbox.py      │
└────────┬─────────┘
         ↓

✅ Done! Agents are public!
```

---

## 📈 Architecture Comparison

### **Local Only:**
```
User → FastAPI (localhost:8080)
         ↓
    Coordinator (localhost:8000)
         ↓
    [6 agents locally]
         ↓
    Response
```

### **Mailbox Agents:**
```
User → FastAPI (localhost:8080)
         ↓
    Coordinator (localhost:8000) ←─┐
         ↓                         │
    [6 agents locally]             │
         ↓                         │
    Response                       │
         ↑                         │
         └── Agentverse Mailbox ───┘
             (Public: agent1q...)
```

### **Hosted Agents:**
```
User → FastAPI (localhost:8080)
         ↓
    Agentverse API
         ↓
    Coordinator (cloud) → agent1q...
         ↓
    [6 agents in cloud]
         ↓
    Response
```

---

## 🎨 Demo Script with Mailbox Agents

### **Opening:**
> "Our system uses **Fetch.ai's Agentverse**, a decentralized agent network. Let me show you..."

### **Show Agentverse Dashboard:**
> "Here are our 7 agents deployed on Agentverse. Each has a public address - these aren't just local scripts, they're globally accessible AI agents."

### **Show Agent Logs:**
```bash
✓ Added coordinator agent: agent1q2w3e4r5t6y7u8i9o0...
✓ Added eligibility agent: agent1q9o8i7u6y5t4r3e2w1...
```

> "See these addresses? Any agent in the world can communicate with ours using these addresses."

### **Run Demo Query:**
```bash
curl -X POST http://localhost:8080/api/match/trial \
  -H "Content-Type: application/json" \
  -d '{"trial_id": "NCT00100000"}'
```

> "Watch as our Coordinator orchestrates all 7 agents... [wait for response] ...and there we go! 4,500 patients matched in under 3 seconds."

### **Explain Architecture:**
> "The beauty is: Conway's heavy ML runs locally on our hardware for speed, but the agents coordinate through Agentverse. This means we could scale this to coordinate trial matching across hospitals worldwide, all through autonomous agent communication."

### **Closing:**
> "Traditional trial enrollment: 6-12 months. Our system with decentralized agents: 8-12 weeks with 87% confidence. That's the power of unsupervised pattern discovery plus multi-agent orchestration."

---

## 🔑 Key Agentverse Concepts

### **Agent Address**
```
agent1q2w3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j8k9l0
│      │                                      │
│      └─ Derived from seed ──────────────── │
└─ "agent1" prefix                           │
                   Unique identifier ────────┘
```

### **Mailbox**
```
Your Laptop                    Agentverse Cloud
    │                               │
    │  1. Local agent sends msg     │
    ├──────────────────────────────>│
    │                               │
    │  2. Mailbox stores msg        │
    │                               │
    │  3. Recipient polls mailbox   │
    │<──────────────────────────────┤
    │                               │
    │  4. Message delivered         │
```

### **Message Flow**
```
Agent A                    Agent B
   │                          │
   │  Send(msg)               │
   ├─────────────────────────>│
   │                          │
   │                     on_query()
   │                          │
   │                      Process
   │                          │
   │                   Return(response)
   │<─────────────────────────┤
   │                          │
 Receive                      │
```

---

## 📊 Resource Requirements

### **Local Only:**
```
CPU: 2-4 cores (for Conway ML)
RAM: 4-8 GB
Network: None required
Time: Instant
```

### **Mailbox Agents:**
```
CPU: 2-4 cores (for Conway ML)
RAM: 4-8 GB
Network: Stable internet required
Time: 5 min setup
```

### **Hosted Agents:**
```
CPU: Provided by Agentverse
RAM: Provided by Agentverse
Network: Internet required
Time: 15-30 min setup
Note: Can't run heavy ML (Conway)
```

---

## ✅ Decision Matrix

Choose **Local Only** if:
- ❌ No internet during demo
- ✓ Just want to test quickly
- ✓ Don't need public access

Choose **Mailbox Agents** if:
- ✓ Want public addresses
- ✓ Need fast execution
- ✓ Have stable internet
- ✓ Doing a hackathon
- ✓ Want to impress judges

Choose **Hosted Agents** if:
- ✓ Production deployment
- ✓ Don't need heavy ML
- ✓ Want always-on agents
- ✓ Have time for setup

---

## 🎯 Final Recommendation

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  BEST SETUP FOR CALHACKS:                                         ║
║                                                                   ║
║  PRIMARY: Mailbox Agents                                          ║
║  - Get public addresses                                           ║
║  - Fast local execution                                           ║
║  - Great for demo                                                 ║
║                                                                   ║
║  BACKUP: Local Only                                               ║
║  - If internet fails during demo                                  ║
║  - Just run: python run_agents.py                                 ║
║  - Everything still works                                         ║
║                                                                   ║
║  COMMANDS:                                                        ║
║  1. python setup_agentverse.py                                    ║
║  2. source .env.agentverse                                        ║
║  3. python run_agents_mailbox.py                                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Setup mailboxes | `python setup_agentverse.py` |
| Load environment | `source .env.agentverse` |
| Run with mailboxes | `python run_agents_mailbox.py` |
| Run local only | `python run_agents.py` |
| Test agents | `python test_agents.py` |
| Check environment | `env \| grep MAILBOX` |

---

## 🎓 Learn More

- **Quick Guide:** [AGENTVERSE_QUICKSTART.md](AGENTVERSE_QUICKSTART.md)
- **Full Guide:** [AGENTVERSE_DEPLOYMENT.md](AGENTVERSE_DEPLOYMENT.md)
- **Agent Docs:** [AGENTS_README.md](AGENTS_README.md)
- **Fetch.ai:** https://docs.fetch.ai

---

**You're ready to deploy! Choose your option and let's go! 🚀**
