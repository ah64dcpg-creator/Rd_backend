# Raising Daisies Backend (GitHub-Ready Root)

This folder is ready to upload straight to GitHub and deploy on Railway.

## Files
- requirements.txt (at repo root)
- railway.json (start command for Railway)
- app/ (FastAPI app with /health, /events, /admin/ingest_bulk)

## Deploy on Railway
1) New Project → Deploy from GitHub → pick this repo
2) Add a Postgres database (Plugin → Postgres)
3) Add Variables:
   - DATABASE_URL = (from Postgres)
   - ADMIN_TOKEN = your secret (e.g., daisy-secret)
   - CORS_ALLOW_ORIGINS = *   (for testing)
4) Deploy → visit /health to test
