import os
import random
import httpx
import asyncio
from sqlalchemy.orm import Session
from ..models import Ward, TrafficData, PollutionSource, AQIReading

WAQI_TOKEN = os.getenv("WAQI_API_KEY")

async def fetch_ward_aqi(ward: Ward):
    """
    Fetches live AQI for a specific ward using coordinates via WAQI API.
    """
    if not WAQI_TOKEN or not ward.latitude or not ward.longitude:
        # Fallback to simulation if no API key or coordinates
        return random.uniform(50, 200)

    url = f"https://api.waqi.info/feed/geo:{ward.latitude};{ward.longitude}/?token={WAQI_TOKEN}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            if data.get("status") == "ok":
                return data["data"]["aqi"]
    except Exception as e:
        print(f"Error fetching AQI for {ward.name}: {e}")
    
    return random.uniform(50, 150) # Final fallback

async def update_live_aqi(db: Session):
    """
    Computes ward-level AQI using live API data or simulation.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_aqi_readings = []
    
    # Fetch all AQIs concurrently
    tasks = [fetch_ward_aqi(ward) for ward in wards]
    aqi_values = await asyncio.gather(*tasks)

    for i, ward in enumerate(wards):
        total_aqi = aqi_values[i]
        
        # Add some local variance based on traffic if available
        latest_traffic = db.query(TrafficData).filter(TrafficData.ward_id == ward.id).order_by(TrafficData.timestamp.desc()).first()
        if latest_traffic:
            # Small traffic impact adjustment (±10%)
            total_aqi += (latest_traffic.emission_index * 0.05)
        
        # Ensure AQI is within a reasonable range, e.g., 0-500
        total_aqi = max(0, min(500, total_aqi))

        ar = AQIReading(
            ward_id=ward.id,
            aqi_value=round(total_aqi, 2)
        )
        db.add(ar)
        new_aqi_readings.append(ar)
    
    db.commit()
    for ar in new_aqi_readings:
        db.refresh(ar)
    
    return new_aqi_readings
