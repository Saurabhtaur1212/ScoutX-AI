<<<<<<< HEAD
# ScoutX AI — Esports Scouting & Multi-Roster Intelligence

A hackathon-ready full-stack prototype for player scouting, role-specific scoring, recruitment recommendations, and multi-game roster management.

## Stack
- Frontend: Next.js (App Router), React, TypeScript, Recharts, Lucide React
- Backend: FastAPI, Pydantic, Pandas
- Demo data: generated, clearly labelled simulated data
- Storage: JSON-backed demo persistence (simple to run locally). Replace with PostgreSQL for production.

## Features
- Dashboard with scouting KPIs and charts
- Player search/filter by game, role, and budget
- Explainable role-specific player scores
- Candidate recommendations for a team/role and budget
- Multi-game teams and roster management
- Player performance trends and comparison view
- Advanced Intelligence workspace (`/intelligence`) with player style matching, meta-adaptability proxy, recruitment value estimate, counterfactual roster analysis, timestamped video evidence, scout feedback capture, data quality checks, and evidence-based reports
- CSV import endpoint
- Simulated-data labels and metric assumptions

## Run locally

### 1. Backend
Requirements: Python 3.10+

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend
Requirements: Node.js 20+

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

Set `NEXT_PUBLIC_API_URL` if backend is not running at `http://localhost:8000`.

## Demo flow
1. Open Dashboard.
2. Go to Scouting and filter by game/role.
3. Open a player to inspect metrics.
4. Open Recommendations, select game, role, budget and team.
5. Review ranked candidates and explanation.
6. Open Rosters to view and manage multi-game teams.

## Metrics and assumptions
Scores are normalized to 0–100 and use transparent heuristic formulas, not trained or validated predictive models.

### Tactical FPS IGL score
`0.30*decision + 0.25*round_conversion + 0.20*coordination + 0.15*tactical_execution + 0.10*consistency`

### Other roles
Role-specific weights are defined in `backend/app/scoring.py`. Metrics that are not directly available from match telemetry (e.g. shot-calling or communication) are simulated in this demo and must be replaced with verified coach annotations or supported data before real-world use.

### Fit score
`0.50*role_score + 0.25*roster_fit + 0.15*synergy + 0.10*budget_suitability`

Candidates outside the requested budget are excluded by default. For demo purposes, simulated budget and player metrics do not represent real athletes or market prices.

## API overview
- `GET /api/health`
- `GET /api/summary`
- `GET /api/players`
- `GET /api/players/{player_id}`
- `GET /api/players/{player_id}/trend`
- `GET /api/recommendations?game=Valorant&role=IGL&budget=600000&team_id=1`
- `GET /api/teams`
- `GET /api/teams/{team_id}`
- `POST /api/teams/{team_id}/members`
- `DELETE /api/teams/{team_id}/members/{player_id}`
- `POST /api/import/csv` (multipart CSV upload with a `file` field)
- `GET /api/intelligence/overview`
- `GET /api/intelligence/style-match/{player_id}`
- `GET /api/intelligence/meta-adaptability/{player_id}`
- `GET /api/intelligence/recruitment-value/{player_id}?budget=600000`
- `POST /api/intelligence/counterfactual?team_id=1&candidate_id=21`
- `GET` / `POST /api/intelligence/video-evidence` (timestamped, manually linked clips)
- `GET` / `POST /api/intelligence/feedback` (stores scout feedback for offline review)
- `GET /api/intelligence/data-quality`
- `GET /api/intelligence/reports/{player_id}`

## Advanced intelligence module

Open **Advanced intelligence** from the sidebar. Select a player and (where relevant) a roster, then choose one of the eight feature tabs. The UI calls the FastAPI endpoints above and supports adding timestamped video observations, recording feedback, reviewing data-quality flags, and exporting a generated scouting report as JSON.

Feature implementation status and caveats:
- Style matching compares shared 0–100 metrics within the same game; it is a similarity heuristic, not proof of identical playstyle.
- Meta adaptability is a proxy until verified patch-by-patch snapshots are collected.
- Recruitment value uses demo estimated costs; it is not a real market valuation.
- Counterfactual analysis compares aggregate roster metrics; it does not predict wins or model true team chemistry.
- Video evidence is manually attached to a URL and timestamp. Automatic video understanding is not implemented.
- Scout feedback is stored for later human review; it does not automatically retrain a model.
- Data-quality checks flag missing, suspicious, low-sample, or low-confidence records. Missing freshness metadata is called out explicitly.
- Scouting reports include top metrics, development areas, linked clips, and limitations.

The current demo persists feedback and video links in JSON files under `backend/data`. This is suitable for local prototyping only; use a transactional database, access controls, and audit logging for multi-user production deployment.

## Production notes
This is a functional prototype, not a production-ready recruitment system. Before production, add real authentication/authorization, PostgreSQL migrations, audit logging, data licensing checks, rate limiting, backups, and validated models. Do not use simulated scores to make real recruitment decisions.
=======
# ScoutX-AI
ScoutX AI is an AI-assisted esports scouting and multi-roster intelligence platform. It helps organizations discover  players, compare game-specific performance, identify role fit, build balanced rosters, and track player development  across multiple titles.  
>>>>>>> 9d93bf71ed2f66a1ac72ae5901d8fbd4117850f6
