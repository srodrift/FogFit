from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx, random, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = FastAPI(title="FogFit")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Use your real domain/email if you have one — NOAA is picky.
NOAA_HEADERS = {
    "User-Agent": os.environ.get("FOGFIT_UA", "FogFit/1.0 (+https://example.com; contact: you@yourdomain.com)"),
    "Accept": "application/geo+json",
    "Cache-Control": "no-cache",
}

# ---- ALL SF NEIGHBORHOODS ----
NEIGHBORHOODS = {
    # Waterfront / Downtown
    "Embarcadero": (37.7950, -122.3960),
    "Financial District": (37.7945, -122.3999),
    "Union Square": (37.7880, -122.4075),
    "Civic Center": (37.7790, -122.4160),
    "Tenderloin": (37.7830, -122.4140),
    "SoMa": (37.7810, -122.4039),
    "South Beach": (37.7837, -122.3880),
    "Rincon Hill": (37.7890, -122.3920),
    "Yerba Buena": (37.7857, -122.4020),
    "North Waterfront": (37.8050, -122.4030),

    # Northeast / Hills
    "Chinatown": (37.7941, -122.4078),
    "North Beach": (37.8061, -122.4100),
    "Telegraph Hill": (37.8024, -122.4058),
    "Russian Hill": (37.8019, -122.4190),
    "Nob Hill": (37.7930, -122.4160),

    # Western Addition / Center
    "Hayes Valley": (37.7763, -122.4240),
    "Lower Haight": (37.7718, -122.4310),
    "Alamo Square": (37.7777, -122.4340),
    "Western Addition": (37.7817, -122.4310),
    "Fillmore": (37.7830, -122.4330),
    "Japantown": (37.7850, -122.4300),

    # Heights / Park-adjacent
    "Haight-Ashbury": (37.7690, -122.4460),
    "Castro / Eureka Valley": (37.7609, -122.4350),
    "Duboce Triangle": (37.7698, -122.4330),
    "Noe Valley": (37.7502, -122.4337),
    "Twin Peaks": (37.7540, -122.4470),
    "Glen Park": (37.7330, -122.4330),
    "Midtown Terrace": (37.7480, -122.4520),

    # Mission & SE
    "Mission": (37.7599, -122.4148),
    "Mission Bay": (37.7718, -122.3910),
    "Potrero Hill": (37.7605, -122.4010),
    "Dogpatch": (37.7573, -122.3880),
    "Bernal Heights": (37.7415, -122.4149),
    "Bayview–Hunters Point": (37.7290, -122.3820),
    "Silver Terrace": (37.7390, -122.3960),
    "Little Hollywood": (37.7130, -122.3950),
    "Visitacion Valley": (37.7150, -122.4000),
    "Portola": (37.7280, -122.4090),

    # Marina / Presidio / Pac Heights
    "Marina": (37.8037, -122.4368),
    "Cow Hollow": (37.7976, -122.4300),
    "Pacific Heights": (37.7924, -122.4380),
    "Lower Pacific Heights": (37.7860, -122.4360),
    "Presidio Heights": (37.7886, -122.4530),
    "The Presidio": (37.7989, -122.4660),
    "Sea Cliff": (37.7880, -122.4940),
    "Lake Street / Lake District": (37.7849, -122.4737),

    # Richmond
    "Inner Richmond": (37.7787, -122.4620),
    "Central Richmond": (37.7800, -122.4720),
    "Outer Richmond": (37.7780, -122.4950),

    # Sunset & Golden Gate Park
    "Inner Sunset": (37.7630, -122.4660),
    "Golden Gate Heights": (37.7530, -122.4700),
    "Central Sunset": (37.7489, -122.4941),
    "Outer Sunset": (37.7530, -122.4940),
    "Parkside": (37.7390, -122.4840),
    "Ocean Beach": (37.7596, -122.5107),

    # Southwest / Lakes / West Portal
    "West Portal": (37.7410, -122.4690),
    "Forest Hill": (37.7470, -122.4630),
    "Saint Francis Wood": (37.7361, -122.4664),
    "Sunnyside": (37.7320, -122.4460),
    "Westwood Park": (37.7268, -122.4531),
    "Westwood Highlands": (37.7342, -122.4516),
    "Stonestown": (37.7310, -122.4760),
    "Merced Manor": (37.7330, -122.4760),
    "Lakeshore": (37.7240, -122.4930),
    "Lake Merced": (37.7140, -122.4930),
    "Ingleside": (37.7200, -122.4540),
    "Ingleside Terraces": (37.7200, -122.4680),
    "Oceanview": (37.7140, -122.4540),

    # Islands
    "Treasure Island": (37.8250, -122.3710),
    "Yerba Buena Island": (37.8170, -122.3660),
}

def _parse_wind_mps(wind_str):
    num = ""
    for ch in str(wind_str):
        if ch.isdigit() or ch == ".": num += ch
        elif num: break
    try: return float(num) / 2.237
    except: return 0.0

def rec_outfit(temp_c, wind_mps, foggy):
    layers = []
    if temp_c < 10: layers += ["puffer jacket", "thermal base layer", "beanie"]
    elif temp_c < 14: layers += ["hoodie or fleece", "light scarf"]
    elif temp_c < 18: layers += ["denim jacket", "long-sleeve tee"]
    elif temp_c < 22: layers += ["t-shirt", "light overshirt or flannel"]
    else: layers += ["tank top", "shorts"]
    wind_mph = wind_mps * 2.237
    if wind_mph > 25: layers.append("hooded shell jacket")
    elif wind_mph > 15: layers.append("windbreaker")
    if foggy:
        layers += random.choice([
            ["water-resistant layer", "beanie"],
            ["light rain jacket", "scarf"],
            ["fog-proof windbreaker"]
        ])
    layers += ["comfortable sneakers", "reusable tote bag"]
    return layers

async def fetch_noaa_hour(lat, lon):
    async with httpx.AsyncClient(timeout=12, http2=False) as client:
        r = await client.get(f"https://api.weather.gov/points/{lat},{lon}", headers=NOAA_HEADERS)
        r.raise_for_status()
        forecast_url = r.json()["properties"]["forecastHourly"]
        fr = await client.get(forecast_url, headers=NOAA_HEADERS)
        fr.raise_for_status()
        hour = fr.json()["properties"]["periods"][0]
    temp_f = float(hour["temperature"]) if hour.get("temperatureUnit") == "F" else float(hour["temperature"]) * 9/5 + 32
    temp_c = (temp_f - 32) * 5/9
    wind_mps = _parse_wind_mps(hour.get("windSpeed", ""))
    return {
        "temp_f": temp_f, "temp_c": temp_c, "wind_mps": wind_mps,
        "short_forecast": hour.get("shortForecast", "—"),
        "detailed": hour.get("detailedForecast", ""),
        "start_iso": hour.get("startTime", ""), "source": "NOAA",
    }

async def fetch_openmeteo_hour(lat, lon):
    url = ( "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,wind_speed_10m,cloudcover,visibility"
            "&forecast_days=1&timezone=auto" )
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    times = data["hourly"]["time"]
    idx = 0
    now_hour = datetime.now().astimezone().replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:00")
    if now_hour in times:
        idx = times.index(now_hour)
    temp_c = float(data["hourly"]["temperature_2m"][idx])
    temp_f = temp_c * 9/5 + 32
    wind_mps = float(data["hourly"]["wind_speed_10m"][idx]) / 3.6  # km/h -> m/s
    cloud = float(data["hourly"].get("cloudcover", [0])[idx])
    vis  = float(data["hourly"].get("visibility", [20000])[idx])
    foggy = (cloud >= 80) or (vis < 6000)
    return {
        "temp_f": temp_f, "temp_c": temp_c, "wind_mps": wind_mps,
        "short_forecast": "Foggy" if foggy else "Partly Cloudy" if cloud >= 40 else "Clear",
        "detailed": f"Cloud {int(cloud)}%, visibility {int(vis)} m",
        "start_iso": times[idx] + ":00", "source": "Open-Meteo",
    }

def offline_hour(lat, lon):
    seed = int(abs(lat*1000) + abs(lon*1000)) % 10000
    rng = random.Random(seed)
    temp_c = rng.uniform(12, 20)
    wind_mps = rng.uniform(2, 8)
    foggy = rng.choice([True, False])
    short = "Foggy" if foggy else rng.choice(["Clear", "Partly Cloudy"])
    return {
        "temp_f": temp_c * 9/5 + 32, "temp_c": temp_c, "wind_mps": wind_mps,
        "short_forecast": short, "detailed": "offline mock",
        "start_iso": datetime.now(timezone.utc).isoformat(),
        "source": "Offline",
    }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    points = [{"name": n, "lat": lat, "lon": lon} for n, (lat, lon) in NEIGHBORHOODS.items()]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "neighborhoods": list(NEIGHBORHOODS.keys()),
            "points": points,
        }
    )

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"

@app.get("/recommend/{hood}", response_class=HTMLResponse)
async def recommend(request: Request, hood: str):
    if hood not in NEIGHBORHOODS:
        return HTMLResponse(f"Unknown neighborhood: {hood}", status_code=404)

    lat, lon = NEIGHBORHOODS[hood]

    if os.environ.get("FOGFIT_OFFLINE") == "1":
        hour = offline_hour(lat, lon)
        noaa_note = "Forced offline mode"
    else:
        try:
            hour = await fetch_noaa_hour(lat, lon)
            noaa_note = "NOAA OK"
        except Exception as e_noaa:
            try:
                hour = await fetch_openmeteo_hour(lat, lon)
                hour["short_forecast"] += " (fallback)"
                noaa_note = f"NOAA failed: {type(e_noaa).__name__}: {e_noaa}"
            except Exception as e_om:
                hour = offline_hour(lat, lon)
                noaa_note = f"NOAA failed: {e_noaa}; Open-Meteo failed: {e_om}; using offline"

    temp_c = hour["temp_c"]
    fog_text = (hour.get("short_forecast","") + " " + hour.get("detailed","")).lower()
    items = rec_outfit(temp_c, hour["wind_mps"], "fog" in fog_text)

    start_iso = hour.get("start_iso")
    try:
        dt_utc = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
        dt_pt = dt_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        last_updated_local = dt_pt.strftime("%a, %b %d · %I:%M %p %Z")
    except Exception:
        last_updated_local = "—"

    ctx = {
        "request": request, "hood": hood,
        "temp_f": round(hour["temp_f"]),
        "wind_mph": round(hour["wind_mps"] * 2.237),
        "forecast": hour.get("short_forecast", "—"),
        "last_updated_local": last_updated_local,
        "items": items,
        "source": hour.get("source", "?"),
        "noaa_note": noaa_note,
    }
    return templates.TemplateResponse("result.html", ctx)
