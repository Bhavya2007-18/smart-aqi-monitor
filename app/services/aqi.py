from sqlalchemy.orm import Session
from ..models import Ward, TrafficData, PollutionSource, AQIReading
import random

def calculate_aqi(db: Session):
    """
    Computes ward-level AQI using traffic emissions, pollution detections, and baseline pollution.
    Generates AQI values between 50 and 400.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_aqi_readings = []
    for ward in wards:
        # Get latest traffic data
        latest_traffic = db.query(TrafficData).filter(TrafficData.ward_id == ward.id).order_by(TrafficData.timestamp.desc()).first()
        
        # Get recent pollution sources (e.g., last 5 minutes, but we'll just check latest for simulation)
        recent_sources = db.query(PollutionSource).filter(PollutionSource.ward_id == ward.id).order_by(PollutionSource.timestamp.desc()).limit(3).all()

        baseline_aqi = random.uniform(50, 100)
        
        traffic_impact = 0
        if latest_traffic:
            traffic_impact = latest_traffic.emission_index * 1.5

        source_impact = 0
        for source in recent_sources:
            if source.source_type == "industrial_emissions":
                source_impact += 50 * source.confidence
            elif source.source_type == "construction_dust":
                source_impact += 30 * source.confidence
            elif source.source_type == "biomass_burning":
                source_impact += 40 * source.confidence
            else:
                source_impact += 20 * source.confidence
        
        total_aqi = baseline_aqi + traffic_impact + source_impact
        # Clip between 50 and 400
        total_aqi = max(50, min(400, total_aqi))

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
