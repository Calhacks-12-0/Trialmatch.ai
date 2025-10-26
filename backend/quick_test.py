"""
Quick test to see what's working
"""
import requests
import time

print("Testing endpoints...")
print()

# Test 1: Health check
print("1. Testing /api/health...")
try:
    r = requests.get("http://localhost:8080/api/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Dashboard metrics
print("2. Testing /api/dashboard/metrics...")
try:
    r = requests.get("http://localhost:8080/api/dashboard/metrics", timeout=5)
    print(f"   Status: {r.status_code}")
    data = r.json()
    print(f"   Active trials: {data.get('active_trials')}")
    print(f"   AI agents: {data.get('ai_agents')}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 3: Patterns (this triggers Conway for first time)
print("3. Testing /api/patterns (this will take 10-30 seconds on first run)...")
print("   Loading ML model and processing 5,000 patients...")
start = time.time()
try:
    r = requests.get("http://localhost:8080/api/patterns", timeout=120)
    elapsed = time.time() - start
    print(f"   Status: {r.status_code}")
    print(f"   Time: {elapsed:.1f}s")
    data = r.json()
    insights = data.get('pattern_insights', [])
    print(f"   Patterns discovered: {len(insights)}")
    if insights:
        print(f"   First pattern: {insights[0].get('description')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"   Error after {elapsed:.1f}s: {e}")

print()

# Test 4: Agent status
print("4. Testing /api/agents/status...")
try:
    r = requests.get("http://localhost:8080/api/agents/status", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

print()
print("=" * 60)
print("If test 3 worked, patterns are now cached!")
print("Try the full demo again: python demo_agents.py")
print("=" * 60)
