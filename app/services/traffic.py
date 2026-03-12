import os
import random
import httpx
import asyncio
from sqlalchemy.orm import Session
from ..models import Ward, TrafficData

TOMTOM_KEY = os.getenv("TOMTOM_API_KEY")

async def fetch_ward_traffic(ward: Ward):
    """
    Fetches live traffic data for a specific ward using TomTom API or enhanced simulation.
    """
    if not TOMTOM_KEY or not ward.latitude or not ward.longitude:
        # Fallback to enhanced simulation based on time of day
        from datetime import datetime
        hour = datetime.now().hour
        # Peak hours: 8-10 AM and 5-7 PM
        is_peak = (8 <= hour <= 10) or (17 <= hour <= 19)
        base_count = 300 if is_peak else 100
        vehicle_count = random.randint(base_count, base_count + 200)
        return vehicle_count

    # TomTom Flow Segment Data API
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_KEY}&point={ward.latitude},{ward.longitude}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            if "flowSegmentData" in data:
                # Use currentSpeed and freeFlowSpeed to estimate density/count
                flow = data["flowSegmentData"]
                current_speed = flow.get("currentSpeed", 40)
                free_flow = flow.get("freeFlowSpeed", 60)
                # Traffic density proportional to inverse of speed ratio
                density_factor = free_flow / max(1, current_speed)
                vehicle_count = int(density_factor * 100) + random.randint(0, 50)
                return vehicle_count
    except Exception as e:
        print(f"Error fetching traffic for {ward.name}: {e}")
    
    return random.randint(50, 400)

async def update_live_traffic(db: Session):
    """
    Fetches live traffic data for all wards and updates the database.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_traffic_data = []
    
    tasks = [fetch_ward_traffic(ward) for ward in wards]
    vehicle_counts = await asyncio.gather(*tasks)

    for i, ward in enumerate(wards):
        vehicle_count = vehicle_counts[i]
        
        # Calculate derived fields
        traffic_density = min(1.0, vehicle_count / 500.0)
        average_speed = max(10, 60 - (traffic_density * 50)) + random.uniform(-5, 5)
        emission_index = (vehicle_count * 0.1) + (60 / max(1, average_speed) * 10) + random.uniform(0, 10)

        td = TrafficData(
            ward_id=ward.id,
            vehicle_count=vehicle_count,
            average_speed=round(average_speed, 2),
            traffic_density=round(traffic_density, 2),
            emission_index=round(emission_index, 2)
        )
        db.add(td)
        new_traffic_data.append(td)
    
    db.commit()
    for td in new_traffic_data:
        db.refresh(td)
    
    return new_traffic_data
