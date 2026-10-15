# Smart House Management System
Full-stack household manager: **React (Vite) + Django REST Framework + JWT**, SQLite by default, MySQL optional.

## Features
Auth (register/login/logout/refresh, profile, change password) · house profile · family members · expenses (search, filter, pagination, receipt upload) · income · budgets with live spent/remaining · bills · tasks · shopping · maintenance · assets · documents (type/size validated) · notifications bell · dashboard with charts · AI assistant (rule-based fallback, replaceable) · CSV reports · Django admin · per-household data isolation.

## Structure
```
backend/  config/ (settings, urls)  core/ (models, serializers, views, services, urls, tests, seed command)
frontend/ src/ (App, pages, components, context, services, modules.js)
docs/API.md
```

## Backend
```
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # admin at http://localhost:8000/admin/
python manage.py seed_demo         # optional demo data
python manage.py runserver
```
**Demo login (after seed_demo):** `demo@smarthouse.com` / `Demo@12345`

### MySQL (optional)
Create DB `smarthouse`, `pip install -r requirements-mysql.txt`, then in `.env` set `DATABASE_ENGINE=mysql` and the DATABASE_* values.

## Frontend
```
cd frontend
copy .env.example .env   # cp on macOS/Linux
npm install
npm run dev              # http://localhost:5173
```

## AI configuration
`core/services.py` → `AIService()` returns `RuleBasedAI` (works offline). To use an external LLM, implement a class with `insights(house)` and `chat(house, question)`, read `settings.AI_API_KEY`, and return it from `AIService()`. The AI only reads data and suggests; it never writes or deletes.

## Tests
`cd backend && python manage.py test`

## Troubleshooting
CORS error → set `CORS_ORIGINS` in backend `.env` to your frontend URL. MySQL install fails on Windows → use SQLite (default).

## GitHub
```
git init && git add . && git commit -m "Smart House Management System"
git branch -M main && git remote add origin <your-repo-url> && git push -u origin main
```

## Not yet implemented / future work
Forgot/reset password email flow, dedicated per-module Django apps, grocery-specific analytics, PDF export beyond browser print, fine-grained member permissions, landing-page sections beyond the essentials.
