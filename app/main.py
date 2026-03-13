from fastapi import FastAPI
import asyncio
import random
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base, SessionLocal
from app.models import Ward
from app.api import endpoints
from app.api import websockets

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables and seed data
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables verified/created.")

        db = SessionLocal()
        if db.query(Ward).count() == 0:
            print("Seeding initial wards...")
            wards_data = [
                {"name": "Knowledge Park III", "lat": 28.4727, "lon": 77.4820},
                {"name": "Pari Chowk",         "lat": 28.4670, "lon": 77.5138},
                {"name": "Alpha 1",             "lat": 28.4789, "lon": 77.5020},
                {"name": "Omega 1",             "lat": 28.4550, "lon": 77.5250},
                {"name": "Delta 1",             "lat": 28.4900, "lon": 77.5150},
            ]
            for w in wards_data:
                db.add(Ward(
                    name=w["name"],
                    latitude=w["lat"],
                    longitude=w["lon"],
                    population_density=random.randint(5000, 20000),
                ))
            db.commit()
            print("Seeding complete.")
        db.close()
    except Exception as e:
        print(f"Startup Initialization Error: {e}")

    # Start background live-data loop
    loop_task = asyncio.create_task(live_data_loop())
    yield
    loop_task.cancel()


app = FastAPI(
    title="Hyper-Local AQI & Pollution Mitigation Dashboard",
    lifespan=lifespan,
)

# CORS — allow requests from any origin (frontend on Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(endpoints.router, prefix="/api")
app.include_router(websockets.router, prefix="/ws")

# Static files and frontend hosting
static_path = os.path.join(os.path.dirname(__file__), "frontend_assets")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    dash_path = os.path.join(static_path, "dashboard.html")
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
    return {"status": "ok", "service": "API", "docs": "/docs"}

@app.get("/pollution")
async def pollution_page():
    return FileResponse(os.path.join(static_path, "pollution_sources.html"))

@app.get("/traffic")
async def traffic_page():
    return FileResponse(os.path.join(static_path, "traffic_simulation.html"))

@app.get("/predictions")
async def predictions_page():
    return FileResponse(os.path.join(static_path, "aqi_predictions.html"))

@app.get("/policy")
async def policy_page():
    return FileResponse(os.path.join(static_path, "policy_engine.html"))

@app.get("/health")
async def health_page():
    return FileResponse(os.path.join(static_path, "citizen_health.html"))

@app.get("/analytics")
async def analytics_page():
    return FileResponse(os.path.join(static_path, "environmental_analytics.html"))

@app.get("/api-status")
async def health_check():
    return {"status": "ok"}


async def live_data_loop():
    """Background simulation loop — runs continuously on Railway."""
    while True:
        try:
            db = SessionLocal()
            from app.services.aqi import update_live_aqi
            from app.services.traffic import update_live_traffic
            await update_live_traffic(db)
            await update_live_aqi(db)
            db.close()
        except Exception as e:
            print(f"Live loop error: {e}")
        await asyncio.sleep(60)
