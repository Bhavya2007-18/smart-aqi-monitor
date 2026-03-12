from fastapi import FastAPI
import asyncio
import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base, SessionLocal
from .api import endpoints, websockets
from .models import Ward # To ensure tables are created

# Core modules
from .services import traffic, pollution, aqi, reinforcement

# Initialize DB (creates tables if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hyper-Local AQI Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")
app.include_router(websockets.router, prefix="/ws")

# Serve UI Static Files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_assets")
app.mount("/assets", StaticFiles(directory=frontend_path), name="assets")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))

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

@app.get("/health")
async def read_health():
    return FileResponse(os.path.join(frontend_path, "citizen_health.html"))

@app.get("/analytics")
async def read_analytics():
    return FileResponse(os.path.join(frontend_path, "environmental_analytics.html"))

# Background Tasks Definition
async def simulate_data_loop():
    """
    Simulation loop to generate synthetic data on schedule.
    Every 5 seconds: Traffic Data
    Every 10 seconds: AQI Values & Pollution Detection
    Dynamic: Mitigation evaluation
    """
    while True:
        try:
            db = SessionLocal()
            
            # Update Traffic (Every 5s tick)
            new_traffic = traffic.simulate_traffic(db)
            
            # Broadcast Traffic Updates
            if new_traffic:
                data = [{"ward_id": t.ward_id, "vehicle_count": t.vehicle_count, "density": t.traffic_density} for t in new_traffic]
                await websockets.manager.broadcast({"type": "traffic_update", "data": data})

            # Check if it's the 10th second tick by storing loop iteration. For simplicity we just run it every 10s using an internal counter.
            # Here we just run AQI and Pollution less frequently by awaiting extra 5.
            await asyncio.sleep(5)
            
            # Tick 2: Update AQI, Pollution, Mitigations
            db = SessionLocal()
            
            new_pollution = pollution.simulate_pollution_detections(db)
            new_aqi = aqi.calculate_aqi(db)
            new_mitigations = reinforcement.generate_mitigations(db)
            
            if new_pollution:
                data = [{"ward_id": p.ward_id, "source_type": p.source_type, "confidence": p.confidence} for p in new_pollution]
                await websockets.manager.broadcast({"type": "pollution_update", "data": data})

            # Broadcast Updates
            if new_aqi:
                data = [{"ward_id": a.ward_id, "aqi": a.aqi_value} for a in new_aqi]
                await websockets.manager.broadcast({"type": "aqi_update", "data": data})
                
            if new_mitigations:
                data = [{"ward_id": m.ward_id, "action": m.action_type} for m in new_mitigations]
                await websockets.manager.broadcast({"type": "mitigation_alert", "data": data})
                
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Simulation loop error: {e}")
            await asyncio.sleep(5)
        finally:
            db.close()
            

@app.on_event("startup")
async def startup_event():
    # Insert some dummy wards if db is empty
    db = SessionLocal()
    if db.query(Ward).count() == 0:
        names = ["Ward 1", "Ward 2", "Ward 3", "Ward 4", "Ward 5"]
        # Basic insert, without geometry for synthetic data simplicity unless needed
        for name in names:
            db.add(Ward(name=name, population_density=random.randint(2000, 15000)))
        db.commit()
    db.close()
    
    # Start the simulation loops in the background
    asyncio.create_task(simulate_data_loop())
    print("Background simulation started.")
