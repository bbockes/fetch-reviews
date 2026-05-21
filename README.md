# fetch-reviews

Fetch and analyze public App Store written reviews for any iOS app.

## Quick start

### Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Try **CookShelf sample report** for an instant demo, or paste any App Store URL.

Optional: set `ANTHROPIC_API_KEY` in `.env` to enable Claude-powered theme assignment (sentiment-aware review classification), quote trimming, and richer theme extraction. Without a key, the app falls back to pattern matching heuristics.

## CLI

```bash
python3 scripts/fetch_reviews.py "https://apps.apple.com/us/app/id6743496454" -o reviews.json --pretty
```

## Project layout

- `backend/` — API: parse URL, fetch reviews, analyze, poll jobs
- `web/` — Mobbin-style UI with expandable theme rows + quotes
- `scripts/fetch_reviews.py` — standalone CLI

See [instructions.md](./instructions.md) for the full build guide.
