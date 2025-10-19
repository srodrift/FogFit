# 🌁 FogFit

FogFit is a fun San Francisco micro-climate outfit recommender built with **FastAPI**, **Jinja2**, and **NOAA Weather API**.

It fetches live hourly forecasts by neighborhood and recommends layers you should wear — powered by real data, wrapped in foggy vibes, and optionally set to *“I Left My Heart in San Francisco”* 🎶.

## Features
- Real-time weather from NOAA
- 60+ San Francisco neighborhoods
- Dynamic outfit suggestions
- Background music and map-based navigation
- Clean responsive interface

## Tech Stack
- **Python 3**
- **FastAPI** for backend
- **Jinja2** for templating
- **HTTPX** for API calls
- **Leaflet.js** + **OpenStreetMap** for map display
- **HTML/CSS/JS** frontend
- Hosted locally or deployable to Render / Vercel / Railway

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" httpx jinja2 tzdata
uvicorn app.main:app --reload --port 8000
# FogFit
