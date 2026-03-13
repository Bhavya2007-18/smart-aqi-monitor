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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables and seed data
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables verified/created.")
        
        # Seed Wards if empty
        db = SessionLocal()
        if db.query(Ward).count() == 0:
            print("Seeding initial wards...")
            wards_data = [
                {"name": "Knowledge Park III", "lat": 28.4727, "lon": 77.4820},
                {"name": "Pari Chowk", "lat": 28.4670, "lon": 77.5138},
                {"name": "Alpha 1", "lat": 28.4789, "lon": 77.5020},
                {"name": "Omega 1", "lat": 28.4550, "lon": 77.5250},
                {"name": "Delta 1", "lat": 28.4900, "lon": 77.5150}
            ]
            for w in wards_data:
                db.add(Ward(
                    name=w["name"], 
                    latitude=w["lat"], 
                    longitude=w["lon"],
                    population_density=random.randint(5000, 20000)
                ))
            db.commit()
            print("Seeding complete.")
        db.close()
    except Exception as e:
        print(f"Startup Initialization Error: {e}")

    # Background tasks (Local only)
    if not os.environ.get("VERCEL"):
        loop_task = asyncio.create_task(live_data_loop())
        yield
        loop_task.cancel()
    else:
        yield

app = FastAPI(
    title="Hyper-Local AQI & Pollution Mitigation Dashboard",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(endpoints.router, prefix="/api")

# Static files and frontend
static_path = os.path.join(os.path.dirname(__file__), "frontend_assets")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "dashboard.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": "serverless" if os.environ.get("VERCEL") else "local"}

async def live_data_loop():
    """Background simulation loop for local development."""
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
