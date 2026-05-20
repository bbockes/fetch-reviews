# fetch_reviews — Build instructions

A practical guide to turning this repo into a **user-facing web app**: paste an App Store URL or ID → fetch written reviews → generate a polished insight report → optionally export PDF.

**Stack recommendation:** Python API (reuse existing fetch logic) + **Next.js** frontend with **[shadcn/ui](https://ui.shadcn.com)**. UI should feel like **[Mobbin](https://mobbin.com)**: calm, minimal, one job per screen, generous whitespace.

---

## What you already have

| Asset | Role |
|--------|------|
| `fetch_reviews.py` | CLI that fetches up to 500 written reviews (US first, then other storefronts). |
| `generate_cookshelf_pdf.py` | Example ReportLab PDF generator (CookShelf sample). |
| Review analysis pattern | Ranked themes, mention counts, short quotes (see CookShelf report). |

**Data limits (be honest in the UI):**

- Public Apple RSS feeds only; **written reviews**, not star-only ratings.
- **~500 reviews max per storefront**; small apps may have far fewer globally.
- Unofficial feed — can change without notice.

---

## Recommended repo layout

```text
fetch_reviews/
├── instructions.md          # this file
├── README.md                # quick start for contributors
├── .env.example
├── backend/                 # Python 3.11+
│   ├── pyproject.toml       # or requirements.txt
│   └── app/
│       ├── main.py          # FastAPI app
│       ├── fetch.py         # logic from fetch_us_reviews.py
│       ├── analyze.py       # LLM theme extraction
│       ├── pdf.py           # PDF export
│       └── models.py        # Pydantic schemas
├── web/                     # Next.js 15+ App Router
│   ├── app/
│   ├── components/
│   │   └── ui/              # shadcn components
│   └── lib/
└── scripts/
    └── fetch_reviews.py     # optional CLI wrapper
```

Keep **backend and web separate** at first. Deploy API and site independently (e.g. Railway/Fly + Vercel).

---

## Phase 0 — Housekeeping (1 hour)

1. **Move** `fetch_reviews.py` → `scripts/fetch_reviews.py` or `backend/app/fetch.py` when you split the monorepo.
2. Add **`.env.example`**:
   ```env
   OPENAI_API_KEY=
   STRIPE_SECRET_KEY=
   STRIPE_WEBHOOK_SECRET=
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Add **`README.md`** with one command to run the CLI and one sentence on what the product does.
4. **Do not commit** `reviews.json`, API keys, or generated PDFs — add them to `.gitignore`.

---

## Phase 1 — Backend API (2–3 days)

### 1.1 FastAPI skeleton

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pydantic httpx
```

**Endpoints (v1):**

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/parse` | Body: `{ "input": "url or id" }` → `{ "app_id": "6743496454" }` |
| `POST` | `/api/reports` | Start job: fetch + analyze → `{ "report_id": "..." }` |
| `GET` | `/api/reports/{id}` | Poll status + result when `complete` |
| `GET` | `/api/reports/{id}/pdf` | Download PDF (paid or preview tier) |

### 1.2 Port fetch logic

- Move `parse_app_id`, `fetch_reviews`, `_load_json_url` into `backend/app/fetch.py`.
- Expose `fetch_reviews(app_id, max_reviews=500, us_only=False) -> list[Review]`.
- Return a **structured response**:
  ```json
  {
    "app_id": "6743496454",
    "review_count": 89,
    "average_rating": 3.69,
    "storefronts": { "us": 63, "gb": 14 },
    "reviews": [ ... ]
  }
  ```

**Best practices:**

- **Sleep between countries** (default 1s) — keep Apple-friendly behavior.
- **Timeout** per HTTP request (30s).
- **Cache** fetch results in memory/Redis keyed by `app_id` for 24h to avoid repeat hammering.
- Log `review_count` and duration; never log full review text in production logs.

### 1.3 Analysis (`analyze.py`)

Use an LLM with a **fixed JSON schema** (not free-form prose) so the UI is predictable:

```json
{
  "summary": { "average_rating": 3.69, "total_reviews": 89, "one_liner": "..." },
  "loves": [{ "mention_count": 20, "title": "...", "quotes": [{ "author": "...", "storefront": "us", "rating": 5, "excerpt": "..." }] }],
  "pain_points": [ ... ],
  "takeaways": [ "...", "..." ]
}
```

**Best practices:**

- Pass **truncated review text** if token limits bite (title + first 400 chars per review).
- Use a **stable theme taxonomy** in the system prompt (ingredient search, pricing, indexing, no full recipes, etc.).
- Validate output with **Pydantic**; retry once on parse failure.
- Store raw LLM JSON + rendered report on the job record.

### 1.4 PDF (`pdf.py`)

- Refactor `generate_cookshelf_pdf.py` to accept `report: Report` + `reviews: list[Review]` (no hard-coded CookShelf).
- Generate on demand when user pays or clicks “Export PDF”.

### 1.5 Async jobs

Fetching 38 storefronts can take **30–90 seconds**. Do not block an HTTP request that long.

**Simple v1:** In-process background task + poll `GET /reports/{id}`.

**Better v1.5:** Redis + worker, or [Inngest](https://www.inngest.com) / BullMQ if you move to Node for workers.

Return statuses: `queued` → `fetching` → `analyzing` → `complete` | `failed`.

---

## Phase 2 — Frontend with shadcn/ui (3–5 days)

### 2.1 Scaffold

```bash
cd web
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false
npx shadcn@latest init
```

When prompted: **New York** style, **Zinc** base color, **CSS variables**, no dark mode required (Mobbin is mostly light; add dark later if you want).

Add components:

```bash
npx shadcn@latest add button input card badge separator skeleton tabs accordion progress toast
```

Optional: `dialog`, `sheet` (mobile preview), `dropdown-menu`.

### 2.2 Mobbin-style UI principles

| Principle | Implementation |
|-----------|----------------|
| **One primary action per screen** | Hero = single URL/ID field + “Analyze” button |
| **Whitespace** | `max-w-2xl` or `max-w-3xl` centered content; `py-24` hero |
| **Neutral palette** | Zinc/stone background `#fafafa`, black text, one accent (e.g. amber/orange for CTAs) |
| **No dashboard clutter** | No sidebar until you have accounts/history |
| **Typography** | `font-sans`, clear hierarchy: `text-4xl font-semibold tracking-tight` → `text-muted-foreground` subcopy |
| **Cards for results** | Each theme = `Card` with badge count + 2–3 quotes |
| **Trust before pay** | Show review count + avg rating **before** checkout |

**Reference flow (3 screens):**

1. **Landing** — Headline, subhead, input, example link (“Try CookShelf”), footer disclaimer.
2. **Processing** — Skeleton cards + `Progress` (“Fetching US reviews…”, “Scanning 12 more regions…”, “Writing report…”).
3. **Report** — Executive summary → rating breakdown → Loves / Pain points (tabs or stacked sections) → CTA “Download PDF” / “Email report”.

### 2.3 Key pages (`app/`)

```text
app/
├── page.tsx              # landing + submit
├── report/[id]/page.tsx  # full web report
├── layout.tsx            # minimal header (logo + “New report”)
└── globals.css           # shadcn tokens, subtle bg
```

**Landing (`page.tsx`) sketch:**

- Centered column, logo/wordmark top-left (minimal header).
- Input: `placeholder="App Store URL or ID — apps.apple.com/.../id123456789"`
- Primary `Button` full-width on mobile, auto on desktop.
- Muted legal line: “Public written reviews only. Not affiliated with Apple.”

**Report page:**

- Sticky top bar: app name (if resolved), `{n} reviews · {avg}★`, buttons `Export PDF` / `Share`.
- `Tabs`: Summary | What users love | Pain points | All reviews.
- Theme cards: `Badge` with mention count, `Accordion` for extra quotes.

### 2.4 API client

`lib/api.ts`:

- `parseApp(input)` → `app_id`
- `createReport(app_id)` → `report_id`
- `getReport(report_id)` → poll until `complete`

Use **React Query** (`@tanstack/react-query`) for polling and cache.

### 2.5 UX details that matter

- **Inline validation** — regex / backend parse before starting a long job.
- **Low-data warning** — if `review_count < 30`, banner: “Only {n} written reviews found; insights may be limited.”
- **Error states** — invalid ID, fetch failed, LLM failed (retry button).
- **Accessibility** — shadcn defaults are solid; ensure focus rings on input and buttons.

---

## Phase 3 — Monetization (after core loop works)

1. **Stripe Checkout** — one-time “Full report + PDF” per `app_id` (or per `report_id`).
2. **Free tier** — web summary only (top 3 themes); paywall for full themes + PDF + JSON download.
3. **Webhook** — `checkout.session.completed` → mark report `paid` → allow PDF route.

**Best practices:**

- Show **price on the paywall**, not only after Stripe.
- Store purchases in DB: `user_email`, `app_id`, `report_id`, `stripe_session_id`.
- Consider **no account v1** — magic link email with report URL.

---

## Phase 4 — Polish & launch

### Performance

- Edge-cache static landing on Vercel.
- Compress JSON responses; paginate “All reviews” in UI (20 per page).

### Legal & trust

- Terms: not affiliated with Apple; analysis for informational purposes.
- Don’t resell raw review dumps — sell **analysis + optional excerpts** (you already quote short lines).
- “Report generated {date} from public App Store feeds.”

### Observability

- Sentry on web + API.
- Track funnel: `submitted` → `fetch_done` → `analysis_done` → `paid`.

### Sample marketing asset

- Keep **CookShelf** as the public demo report (with permission/disclaimer) so visitors see quality before paying.

---

## Suggested build order (checklist)

- [ ] Rename CLI → `scripts/fetch_reviews.py`, document in README
- [ ] FastAPI: `POST /api/parse`, `POST /api/reports`, `GET /api/reports/{id}`
- [ ] Port fetch logic; return `review_count` + storefront breakdown
- [ ] LLM analysis with JSON schema + Pydantic validation
- [ ] Next.js + shadcn: landing + progress + report view
- [ ] Wire polling from web → API
- [ ] Generalize PDF generator; hook to `GET .../pdf`
- [ ] Stripe paywall on PDF + full report
- [ ] Deploy backend + web; set `NEXT_PUBLIC_API_URL`
- [ ] CookShelf demo report linked from landing

---

## Commands cheat sheet

**CLI (today):**

```bash
python3 scripts/fetch_reviews.py "https://apps.apple.com/us/app/id6743496454" -o reviews.json --pretty
```

**Backend (target):**

```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

**Frontend (target):**

```bash
cd web && npm run dev
```

**PDF sample:**

```bash
python3 scripts/generate_report_pdf.py --input reviews.json --output report.pdf
```

---

## What not to do early

- Don’t build user accounts, teams, or “monitor daily” until one-shot reports sell.
- Don’t promise “all reviews ever” — cap language is a feature.
- Don’t skip the **preview stats** step (count + avg rating) before payment.
- Don’t use a busy admin template — stay Mobbin-minimal until you have retention data.

---

## Questions to decide soon

1. **Brand name** — `fetch_reviews` is descriptive; product name can differ on the landing page.
2. **Price point** — $19 / $29 / $49 per report (validate with 5 manual sales first).
3. **LLM provider** — OpenAI vs Anthropic; pick one and standardize on structured outputs.

When you’re ready to implement, start with **Phase 1 endpoints + Phase 2 landing/report UI** without Stripe; add payments once a friend can run a report end-to-end from the browser.
