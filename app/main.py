from fastapi import FastAPI
import asyncio
import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base, SessionLocal
from app.api import endpoints, websockets
from app.models import Ward # To ensure tables are created

# Core modules
from app.services import traffic, pollution, aqi, reinforcement

# Initialize DB happens in startup_event

# Serve UI Static Files
frontend_path = os.path.join(os.path.dirname(__file__), "frontend_assets")

app = FastAPI(title="Hyper-Local AQI Dashboard Backend")

# Global Exception Handler to prevent 500 screens
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"CRITICAL ERROR: {exc}")
    try:
        return FileResponse(os.path.join(frontend_path, "dashboard.html"))
    except Exception:
        return {"error": "Internal Server Error", "detail": str(exc)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")
app.include_router(websockets.router, prefix="/ws")

try:
    if os.path.exists(frontend_path):
        app.mount("/assets", StaticFiles(directory=frontend_path), name="assets")
except Exception as e:
    print(f"Warning: Static files mount failed: {e}")

@app.get("/")
async def read_root():
    try:
        return FileResponse(os.path.join(frontend_path, "dashboard.html"))
    except Exception:
        return {"status": "ok", "message": "Dashboard loading..."}

@app.get("/pollution")
async def read_pollution():
    return FileResponse(os.path.join(frontend_path, "pollution_sources.html"))

@app.get("/traffic")
async def read_traffic():
    return FileResponse(os.path.join(frontend_path, "traffic_simulation.html"))

@app.get("/predictions")
async def read_predictions():
    return FileResponse(os.path.join(frontend_path, "aqi_predictions.html"))

@app.get("/policy")
async def read_policy():
    return FileResponse(os.path.join(frontend_path, "policy_engine.html"))

@app.get("/citizen-health")
async def read_health_html():
    return FileResponse(os.path.join(frontend_path, "citizen_health.html"))

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/analytics")
async def read_analytics():
    return FileResponse(os.path.join(frontend_path, "environmental_analytics.html"))

@app.get("/api/health")
def api_health():
    return {"status": "ok"}

@app.get("/health_check")
def health_check():
    return {"status": "ok"}


# Background Tasks Definition
async def live_data_loop():
    """
    Background loop to fetch live data or generate realistic simulation.
    Updates traffic every 30s, AQI and others every 60s.
    """
    tick = 0
    while True:
        try:
            db = SessionLocal()
            
            # Update Traffic (Every tick - 30s)
            new_traffic = await traffic.update_live_traffic(db)
            
            # Broadcast Traffic Updates
            if new_traffic:
                data = [{"ward_id": t.ward_id, "vehicle_count": t.vehicle_count, "density": t.traffic_density} for t in new_traffic]
                await websockets.manager.broadcast({"type": "traffic_update", "data": data})

            # Every 2nd tick (60s): Update AQI, Pollution, Mitigations
            if tick % 2 == 0:
                new_pollution = pollution.simulate_pollution_detections(db)
                new_aqi = await aqi.update_live_aqi(db)
                new_mitigations = reinforcement.generate_mitigations(db)
                
                if new_pollution:
                    data = [{"ward_id": p.ward_id, "source_type": p.source_type, "confidence": p.confidence} for p in new_pollution]
                    await websockets.manager.broadcast({"type": "pollution_update", "data": data})

                if new_aqi:
                    data = [{"ward_id": a.ward_id, "aqi": a.aqi_value} for a in new_aqi]
                    await websockets.manager.broadcast({"type": "aqi_update", "data": data})
                    
                if new_mitigations:
                    data = [{"ward_id": m.ward_id, "action": m.action_type} for m in new_mitigations]
                    await websockets.manager.broadcast({"type": "mitigation_alert", "data": data})
                
            tick += 1
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Live data loop error: {e}")
            await asyncio.sleep(10)
        finally:
            db.close()
            

@app.on_event("startup")
async def startup_event():
    try:
        # Initialize DB (creates tables if they don't exist)
        Base.metadata.create_all(bind=engine)
        
        # Insert Greater Noida Wards if db is empty
        db = SessionLocal()
        if db.query(Ward).count() == 0:
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
        db.close()
    except Exception as e:
        print(f"Startup DB Error: {e}")
    
    # Start the live data loop in the background (only if not on Vercel)
    if not os.environ.get("VERCEL"):
        asyncio.create_task(live_data_loop())
        print("Background live data tracking started.")
    else:
        print("Running in Serverless mode (Vercel). Background tasks disabled.")
