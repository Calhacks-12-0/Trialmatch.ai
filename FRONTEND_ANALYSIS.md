# Frontend Analysis - TrialMatch AI Dashboard

## Overview

React + TypeScript dashboard built with Vite, Tailwind CSS, and shadcn/ui components.

**Frontend is now running at**: http://localhost:5173

## Architecture

```
React Frontend (Port 5173)
    ↓
FastAPI Backend (Port 8080)
    ↓
Integration Service
    ↓
Conway Pattern Engine + 7 Fetch.ai Agents
    ↓
ClinicalTrials.gov API
```

## Current Features

### 6 Main Tabs

1. **Dashboard** - Overview metrics and charts
2. **Dataset** - Data source information
3. **Patterns** - Conway pattern visualization (UMAP scatter plot)
4. **Agents** - AI agent status
5. **Matches** - Patient matching results
6. **Sites** - Site selection (placeholder)

### Key Functionality

#### ✅ Working Features

**1. Add Trial Button** (Line 110-117)
- Header button to add new clinical trials
- Opens modal dialog for NCT ID input

**2. Modal Dialog** (Line 123-188)
- Custom modal (not using Radix Dialog)
- Input for trial NCT ID (e.g., NCT05706298)
- "Match Patients" button with loading state
- Cancel button

**3. API Integration** (Line 54-85)
- **Current**: Calls `POST /api/match/trial` (simple matcher)
- Fetches data and adds to `allTrialResults` state
- Switches to "Matches" tab after successful match
- Error handling with alerts

**4. Matches View** (Line 970-1124)
- Displays all matched trials
- Expandable cards showing top 10 patients
- Match scores with progress bars
- Responsive design (desktop table + mobile cards)

**5. Patterns View** (Line 642-923)
- Fetches patterns from `GET /api/patterns`
- UMAP scatter plot visualization (Recharts)
- Pattern filters
- Loading state

## Current API Usage

### Endpoints Used

| Endpoint | Method | Usage | Line |
|----------|--------|-------|------|
| `/api/match/trial` | POST | Match patients (simple) | 59 |
| `/api/patterns` | GET | Get Conway patterns | 654 |

### NOT Using Yet

- ❌ `/api/match/trial/agents` - Full agent pipeline
- ❌ `/api/dashboard/metrics` - Real-time metrics
- ❌ `/api/agents/status` - Agent status

## What Needs to Be Added

### 1. Agent Pipeline Integration

**Current Problem**: Frontend only uses simple matcher, not your 7 agents.

**Line 59**: Change this:
```typescript
const response = await fetch("http://localhost:8080/api/match/trial", {
```

**To**:
```typescript
const response = await fetch("http://localhost:8080/api/match/trial/agents", {
```

**Impact**: Will use full Conway + Agent pipeline instead of simple rule-based matching.

### 2. Display Agent Results

**Current Problem**: Agent response data not displayed.

**Agent Response Structure**:
```json
{
  "status": "success",
  "processing_time": "45.23 seconds",
  "statistics": {
    "total_patients": 1000,
    "patterns_discovered": 27,
    "clustered_patients": 934
  },
  "agent_results": {
    "agents_activated": [...7 agents...],
    "messages_processed": 189,
    "eligible_patients_found": 127,
    "predicted_enrollment_timeline": "8-12 weeks",
    "confidence_score": 0.87
  }
}
```

**Where to Display**:
- Show agent status in Agents tab (Line 925-968)
- Show pattern statistics in Matches view
- Show processing time and confidence score

### 3. Real-Time Agent Status

**Current**: Agents tab shows hardcoded data (Line 927-936)

**Should**: Fetch from `/api/agents/status` endpoint

### 4. Pattern Insights Enhancement

**Current**: Basic pattern display

**Should**: Show more Conway insights:
- Success rates per pattern
- Common conditions in each pattern
- Age distribution
- Match quality scores

### 5. Loading States

**Current**: Simple "Matching..." loader

**Should**:
- Show "Running Conway pattern discovery..."
- Show "Agent coordination in progress..."
- Show individual agent progress

### 6. Error Handling

**Current**: Generic `alert()` on error (Line 81)

**Should**:
- Toast notifications
- Better error messages
- Retry functionality

## File Structure

```
frontend/src/
├── App.tsx                      # Main app (1189 lines)
│   ├── DashboardView()          # Metrics + charts
│   ├── DatasetView()            # Data sources
│   ├── PatternsView()           # Conway patterns
│   ├── AgentsView()             # Agent status
│   ├── MatchesView()            # Trial matches
│   └── SitesView()              # Site selection
│
├── components/
│   ├── ui/                      # shadcn/ui components
│   │   ├── tabs.tsx
│   │   ├── card.tsx
│   │   ├── button.tsx
│   │   └── ...
│   │
│   ├── AgentControl.tsx         # Not used in App.tsx
│   ├── Dashboard.tsx            # Not used in App.tsx
│   ├── PatientMatches.tsx       # Not used in App.tsx
│   ├── PatternDiscovery.tsx     # Not used in App.tsx
│   └── SiteSelection.tsx        # Not used in App.tsx
│
├── main.tsx                     # Entry point
└── index.css                    # Global styles
```

**Note**: The separate component files are not imported into App.tsx - all views are defined inline as functions.

## Key State Variables

```typescript
const [activeTab, setActiveTab] = useState("dashboard");           // Current tab
const [dialogOpen, setDialogOpen] = useState(false);               // Modal open/close
const [trialId, setTrialId] = useState("");                        // NCT ID input
const [isLoading, setIsLoading] = useState(false);                 // Loading state
const [allTrialResults, setAllTrialResults] = useState<any[]>([]); // All matched trials
```

## Dependencies

From package.json:
- **React 18** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Charts (Line chart, Bar chart, Scatter plot)
- **Radix UI** - Component primitives (Tabs, Card, etc.)
- **Lucide React** - Icons

## Next Steps for Integration

### Priority 1: Use Agent Endpoint
1. Change API endpoint to `/api/match/trial/agents` (Line 59)
2. Update loading text to show agent pipeline stages
3. Test with real NCT ID

### Priority 2: Display Agent Results
1. Parse `agent_results` from response
2. Show in Agents tab (real-time status)
3. Show pattern statistics in Matches view
4. Display confidence scores and timeline predictions

### Priority 3: Enhance Visualizations
1. Add agent activity chart
2. Show pattern-to-trial matching scores
3. Display enrollment timeline prediction
4. Show geographic distribution from Site Agent

### Priority 4: Better UX
1. Replace `alert()` with toast notifications
2. Add progress indicators for each agent
3. Show real-time agent messages
4. Add retry/cancel functionality

## Testing the Frontend

**Current Flow**:
1. Open http://localhost:5173
2. Click "Add Trial" button
3. Enter NCT ID (e.g., NCT05613530)
4. Click "Match Patients"
5. View results in Matches tab

**After Integration**:
- Same flow, but will use 7 agents
- Show Conway pattern discovery
- Display agent coordination status
- Show comprehensive results

## Color Scheme

- **Primary Blue**: `#0B5394` (headers, main actions)
- **Success Green**: `#52C41A` (positive metrics, progress)
- **Purple**: `#6B46C1` (agents, AI features)
- **Background**: `#F5F7FA` (light gray)

## API Call Format

**Simple Matcher** (current):
```typescript
fetch("http://localhost:8080/api/match/trial", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ trial_id: "NCT05613530" })
})
```

**Agent Pipeline** (to implement):
```typescript
fetch("http://localhost:8080/api/match/trial/agents", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ trial_id: "NCT05613530" })
})
```

## Summary

**Frontend is functional** with:
- ✅ 6-tab dashboard
- ✅ Add trial modal
- ✅ Pattern visualization
- ✅ Match display
- ✅ Responsive design

**Needs integration with**:
- ❌ Your 7 Fetch.ai agents
- ❌ Full Conway pipeline
- ❌ Real-time agent status
- ❌ Enhanced visualizations

**Main change needed**:
Line 59 in App.tsx - change endpoint from `/api/match/trial` to `/api/match/trial/agents`

---

**Frontend is now running at**: http://localhost:5173
**Ready for agent integration!**
