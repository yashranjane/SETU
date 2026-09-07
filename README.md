# SETU - Innovation Procurement OS

> **The Innovation Procurement Operating System for Smart India Hackathon**  
> Bridging public/enterprise challenges with high-impact startup innovations through AI vector matching, transparent procurement pipelines, and automated RFP generation.

---

## 🚀 Deploy to Render

Deploy the complete SETU portal live on Render with 1-click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yashranjane/SETU)

### Quick Manual Deployment on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) &rarr; Click **New +** &rarr; **Web Service**.
2. Connect your GitHub repo (`yashranjane/SETU`).
3. Set **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`
   - **Health Check Path**: `/health`
4. Set Environment Variable:
   - `RESET_DB`: `true` (initializes clean baseline with only the Stormwater challenge)
5. Click **Create Web Service** &mdash; your portal will be live in minutes!

---

## Monorepo Architecture

```
setu/
├── .antigravity/
│   └── rules.json            # Governance: strict typing, forbidden LLM APIs & mainnets
├── api/                      # Python FastAPI Service
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py     # Settings (DB_URL, JWT_SECRET, CORS_ORIGINS)
│   │   └── main.py           # Application entrypoint & routes
│   ├── Dockerfile            # Python 3.11 with Weasyprint & Postgres runtime
│   ├── requirements.txt      # Pinned dependencies
│   └── .env.example
├── web/                      # Next.js 14+ Frontend (App Router)
│   ├── src/
│   │   └── app/
│   │       ├── globals.css   # Tailwind CSS setup
│   │       ├── layout.tsx    # Root layout
│   │       └── page.tsx      # Landing & Dashboard UI
│   ├── Dockerfile            # Node 20 runtime
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.mjs
└── docker-compose.yml        # PostgreSQL 16 + pgvector, API, and Web
```

---

## Quick Start (Docker Compose)

Run the entire stack with a single command:

```bash
docker compose up --build
```

- **Web Frontend**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **PostgreSQL + pgvector**: `localhost:5432` (`db: setu_db`, `user: postgres`, `password: postgres`)

---

## Local Development (Without Docker)

### 1. API Backend (Python)
```bash
cd api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Web Frontend (Next.js)
```bash
cd web
npm install
npm run dev
```
