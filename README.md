# 🌁 FogFit

[![Open in Hugging Face Spaces](https://img.shields.io/badge/🚀%20View%20Live%20Demo%20on%20Hugging%20Face-blue?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/srodrift/FogFit)

A San Francisco–themed weather and vibe visualization app built with **FastAPI**, **Jinja2**, and **Uvicorn**, deployed on **Hugging Face Spaces**.  
🎶 Plays Tony Bennett’s *“I Left My Heart in San Francisco”* while showing live weather moods by neighborhood.

---

## 🌤️ Overview

FogFit blends the **local spirit of San Francisco** with real-time weather updates to give each neighborhood its own vibe.  
From **foggy Twin Peaks** to **sunny Mission District**, it’s a playful, ambient project that celebrates microclimates, art, and data.

---

## 🏙️ Features

- 🌡️ **Live weather data** using public APIs  
- 🗺️ **Neighborhood-level mapping** — 70+ SF neighborhoods included  
- 🎶 **Background soundtrack** (*“I Left My Heart in San Francisco”*)  
- 🎨 **Golden Gate–themed background image**  
- ⚡ **FastAPI + Jinja2** dynamic rendering  
- ☁️ **Deployed on Hugging Face Spaces (Docker)**

---

## 🧠 Tech Stack

| Category | Tools |
|-----------|-------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/) |
| Frontend | HTML, CSS, Jinja2 templates |
| Deployment | [Hugging Face Spaces](https://huggingface.co/spaces) (Docker) |
| Version Control | Git + GitHub |
| Media | MP3 (background music), static images |
| Language | Python 3.9+ |

---

## 🗺️ Neighborhood Coverage

Includes **every San Francisco neighborhood**, from the waterfront to the hills —  
like *Laurel Heights*, *Excelsior*, *Visitacion Valley*, *Red Rock Hill*, and more.

---

## 🚀 Run Locally

Clone and run FogFit on your own machine:

```bash
git clone https://github.com/srodrift/FogFit.git
cd FogFit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
