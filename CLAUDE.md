# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a healthcare clinical trial matching dashboard called **TrialMatch AI**, built with React, TypeScript, and Vite. The application uses AI agents to analyze patient data, discover patterns, match patients to clinical trials, and select optimal trial sites. Originally exported from a Figma design and uses shadcn/ui components.

## Build & Development Commands

```bash
# Install dependencies
npm i

# Start development server (runs on port 3000, auto-opens browser)
npm run dev

# Build for production (outputs to build/ directory)
npm run build
```

## Architecture

### Entry Point
- `index.html` → loads `/src/main.tsx` as module entry
- `src/main.tsx` → renders `<App />` into `#root`
- `src/App.tsx` → main application shell with tab navigation

### Component Structure

The app uses a **tab-based navigation** system with 5 main views:
1. **Dashboard** - Metrics overview, enrollment trends, trial activity
2. **Pattern Discovery** - Scatter plot visualization of patient patterns with filters
3. **Agent Control** - AI agent orchestration network with hexagon visualization
4. **Patient Matches** - Detailed patient-trial matching table with scoring
5. **Site Selection** - Trial site map and capacity management

**Key Components:**
- `src/components/Dashboard.tsx` - Main dashboard with metrics cards, line charts (Recharts), and AI agent status grid
- `src/components/PatternDiscovery.tsx` - Scatter plot with interactive filters for discovering patient patterns
- `src/components/AgentControl.tsx` - Hexagon network diagram showing real-time AI agent activity with live log feed
- `src/components/PatientMatches.tsx` - Data table with sortable columns, match scores, pie charts for distribution
- `src/components/SiteSelection.tsx` - Site selection and capacity visualization
- `src/components/ui/*` - shadcn/ui components (buttons, cards, tables, charts, forms, etc.)

### Data Flow
- All data is currently **static/mock data** defined within each component
- Components use React `useState` for local state management
- No external API calls or backend integration yet
- Charts use Recharts library (LineChart, ScatterChart, PieChart)

### Styling
- **Tailwind CSS** for utility classes (via `src/index.css` and `src/styles/globals.css`)
- shadcn/ui components with customizable variants
- Color scheme:
  - Primary Blue: `#0B5394`
  - Success Green: `#52C41A`
  - Purple: `#6B46C1`
  - Background: `#F5F7FA`

## Build Configuration

- **Vite** with SWC React plugin for fast builds
- TypeScript with `.tsx` support
- Path alias: `@/` maps to `src/`
- Extensive version-specific package aliases in vite.config.ts for Figma compatibility
- Server runs on port 3000 with auto-open

## Important Notes

- Components use extensive Radix UI primitives via shadcn/ui
- The app is a visual prototype - backend integration would be needed for production use
- All trial data (NCT numbers, patient records, agent activity) is mocked
- The "AI Agents" visualizations simulate agent activity with timers and random messages
