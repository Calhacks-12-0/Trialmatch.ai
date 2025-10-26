# ⚡ Quick Setup Guide - Python 3.12

## ✅ What We Fixed

**Problem:** uagents requires Python <3.13, but you had Python 3.13
**Solution:** Installed Python 3.12 and created virtual environment

---

## 🚀 Quick Start (You're Already Set Up!)

Your environment is ready to go! Just activate it and run:

```bash
cd /Users/brandon/Desktop/CalHacks12/Healthcaredashboarddesign/backend

# Activate virtual environment
source venv/bin/activate

# Run agents
python run_agents.py
```

You should see:
```
✓ Coordinator Agent started: agent1q0t5...
✓ Eligibility Agent started: agent1qdd8...
✓ Pattern Agent started: agent1qt59...
✓ Discovery Agent started: agent1qfd0...
✓ Matching Agent started: agent1q2q2...
✓ Site Agent started: agent1qg5m4...
✓ Prediction Agent started: agent1qt43...
```

---

## 📦 What's Installed

Your `venv` has all dependencies:

**Core:**
- ✅ `uagents==0.12.2` (Fetch.ai framework)
- ✅ `pydantic==1.10.9` (required for uagents)
- ✅ `fastapi==0.120.0`
- ✅ `uvicorn==0.20.0`

**ML:**
- ✅ `pandas==2.3.3`
- ✅ `numpy==2.3.4`
- ✅ `scikit-learn==1.7.2`
- ✅ `sentence-transformers==5.1.2`
- ✅ `umap-learn==0.5.9`
- ✅ `hdbscan==0.8.40`
- ✅ `torch==2.9.0`

---

## 🎯 Commands

### **Start Agents:**
```bash
source venv/bin/activate
python run_agents.py
```

### **Start FastAPI Backend** (in another terminal):
```bash
source venv/bin/activate
python app.py
```

### **Run Tests:**
```bash
source venv/bin/activate
python test_agents.py
```

### **Setup Agentverse:**
```bash
source venv/bin/activate
python setup_agentverse.py
```

---

## 🔧 For Your Teammates

If your teammates need to set up:

```bash
cd backend

# Install Python 3.12 (if needed)
brew install python@3.12

# Create venv with Python 3.12
/opt/homebrew/bin/python3.12 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install uagents pydantic==1.10.9
pip install fastapi pandas numpy scikit-learn sentence-transformers umap-learn hdbscan

# Run!
python run_agents.py
```

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError: No module named 'uagents'"**

Make sure you activated the venv:
```bash
source venv/bin/activate
python --version  # Should show Python 3.12.12
```

### **"Python 3.13 not compatible"**

You need Python 3.12 or 3.11:
```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **"Port already in use"**

Kill existing agents:
```bash
pkill -f "python run_agents"
# or
lsof -ti:8000,8001,8002,8003,8004,8005,8006 | xargs kill -9
```

---

## ✅ You're Ready!

Your setup is complete. Run the agents:

```bash
source venv/bin/activate
python run_agents.py
```

Then in another terminal:

```bash
source venv/bin/activate
python app.py
```

Test it:

```bash
curl http://localhost:8080/api/health
```

🎉 **You're good to go!**
