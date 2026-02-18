# Airbnb Maintenance Tracker

Capstone project for tracking Airbnb property maintenance.

## What It Does

- Manage properties, maintenance contacts, and tasks
- Track task cost, paid/unpaid, complete/incomplete, notes, and recurring tasks
- Basic reporting (paid/unpaid totals and a simple yearly projection)
- Login support via Supabase Auth

## Tech

- Python + Flask (API + server-rendered pages)
- Supabase (hosted Postgres + Auth)
- HTML/CSS/JS (simple single-page UI)

## Run Locally

1) Create and activate a virtual environment

2) Install dependencies

```bash
python -m pip install -r requirements.txt
```

3) Set environment variables

Windows (PowerShell):

```powershell
$env:SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
$env:SUPABASE_KEY = "YOUR_SERVICE_ROLE_KEY"
$env:SECRET_KEY = "change-me"
```

4) Run the app

```bash
python -m airbnb_maintenance.cloud_web_app
```

Open: `http://localhost:5000`

## Supabase Setup Notes

- Create the `properties`, `contacts`, and `tasks` tables
- Add `user_id` columns and enable Row Level Security (RLS) so each user only sees their own data

## Deploy

This repo is set up to deploy to Render as a Web Service.

## Repository

GitHub: `https://github.com/JamesACIV/AirBnb-Maintenence-Tracker`
