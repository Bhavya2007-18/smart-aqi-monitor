from sqlalchemy.orm import Session
from app.models import Ward, AQIReading, TrafficData, PollutionSource
from datetime import datetime, timedelta
import random

def get_hotspots(db: Session):
    """
    Feature 1: Pollution Hotspot Detection Engine
    AQI of ward > 1.5 x average AQI of all wards.
    """
    wards = db.query(Ward).all()
    if not wards: return []
    
    # Get latest AQIs
    latest_readings = []
    for w in wards:
        latest = db.query(AQIReading).filter(AQIReading.ward_id == w.id).order_by(AQIReading.timestamp.desc()).first()
        if latest:
            latest_readings.append(latest)
    
    if not latest_readings: return []
    
    avg_aqi = sum(r.aqi_value for r in latest_readings) / len(latest_readings)
    hotspots = []
    
    for r in latest_readings:
        if r.aqi_value > 1.5 * avg_aqi:
            # Determine dominant source
            top_source = db.query(PollutionSource).filter(PollutionSource.ward_id == r.ward_id).order_by(PollutionSource.timestamp.desc()).first()
            source_name = top_source.source_type if top_source else "unknown"
            
            severity = "high" if r.aqi_value > 300 else "moderate"
            
            hotspots.append({
                "ward_id": r.ward_id,
                "status": "pollution_hotspot",
                "severity": severity,
                "dominant_source": source_name
            })
    return hotspots

def get_pollution_events(db: Session):
    """
    Feature 2: Pollution Event Detector
    Increase > 40 points within 10 minutes.
    """
    wards = db.query(Ward).all()
    events = []
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    
    for ward in wards:
        # Get latest and one from ~10 mins ago
        latest = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).first()
        past = db.query(AQIReading).filter(
            AQIReading.ward_id == ward.id, 
            AQIReading.timestamp <= ten_mins_ago
        ).order_by(AQIReading.timestamp.desc()).first()
        
        if latest and past:
            diff = latest.aqi_value - past.aqi_value
            if diff > 40:
                # Classify event
                cause = "traffic congestion"
                # Check for recent specific sources
                recent_ps = db.query(PollutionSource).filter(
                    PollutionSource.ward_id == ward.id,
                    PollutionSource.timestamp >= ten_mins_ago
                ).first()
                if recent_ps:
                    if recent_ps.source_type == "construction_dust": cause = "construction dust surge"
                    elif recent_ps.source_type == "biomass_burning": cause = "biomass burning event"
                
                events.append({
                    "event_type": "sudden_pollution_spike",
                    "ward_id": ward.id,
                    "aqi_before": past.aqi_value,
                    "aqi_after": latest.aqi_value,
                    "probable_cause": cause
                })
    return events

def get_health_risks(db: Session):
    """
    Feature 3: Citizen Exposure Risk Index
    Based on AQI and population density.
    """
    wards = db.query(Ward).all()
    risks = []
    for ward in wards:
        latest = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).first()
        if not latest: continue
        
        # Risk factor = AQI * Population Density (normalized pseudo-score)
        # Using a simple categorical logic
        aqi = latest.aqi_value
        density = ward.population_density or 5000 # default
        
        score = (aqi / 100) * (density / 5000)
        
        if score > 4.0 or aqi > 300:
            level, action = "Severe Risk", "Stay indoors, use air purifiers"
        elif score > 2.5 or aqi > 200:
            level, action = "High Risk", "Avoid outdoor exercise"
        elif score > 1.5 or aqi > 100:
            level, action = "Moderate Risk", "Limit prolonged outdoor exertion"
        else:
            level, action = "Low Risk", "Safe for outdoor activities"
            
        risks.append({
            "ward_id": ward.id,
            "risk_level": level,
            "recommended_action": action
        })
    return risks

def get_source_probability(db: Session):
    """
    Feature 4: Pollution Source Probability Analyzer
    Rule-based scoring.
    """
    wards = db.query(Ward).all()
    results = []
    for ward in wards:
        traffic = db.query(TrafficData).filter(TrafficData.ward_id == ward.id).order_by(TrafficData.timestamp.desc()).first()
        pollution = db.query(PollutionSource).filter(PollutionSource.ward_id == ward.id).order_by(PollutionSource.timestamp.desc()).first()
        
        t_score = (traffic.traffic_density if traffic else 0.5) * 10
        c_score = 5 if (pollution and pollution.source_type == "construction_dust") else 2
        b_score = 4 if (pollution and pollution.source_type == "biomass_burning") else 1
        
        total = t_score + c_score + b_score
        
        results.append({
            "ward_id": ward.id,
            "source_probability": {
                "traffic_emission": round(t_score / total, 2),
                "construction_dust": round(c_score / total, 2),
                "biomass_burning": round(b_score / total, 2)
            }
        })
    return results

def get_pollution_ranking(db: Session):
    """
    Feature 6: City Pollution Ranking System
    Sort by AQI descending.
    """
    wards = db.query(Ward).all()
    data = []
    for ward in wards:
        latest = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).first()
        if latest:
            data.append({"ward_id": ward.id, "aqi": latest.aqi_value})
    
    # Sort
    data.sort(key=lambda x: x['aqi'], reverse=True)
    for i, item in enumerate(data):
        item['rank'] = i + 1
    return data

def get_emergency_status(db: Session):
    """
    Feature 8: Emergency Pollution Mode
    AQI > 350.
    """
    wards = db.query(Ward).all()
    results = []
    for ward in wards:
        latest = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).first()
        if latest and latest.aqi_value > 350:
            results.append({
                "ward_id": ward.id,
                "emergency_mode": True,
                "actions": ["halt_construction", "restrict_trucks", "public_alert"]
            })
        else:
            results.append({
                "ward_id": ward.id,
                "emergency_mode": False,
                "actions": []
            })
    return results

def get_trends(db: Session):
    """
    Feature 9: Pollution Trend Intelligence
    """
    wards = db.query(Ward).all()
    results = []
    for ward in wards:
        # High level mock patterns for simulation
        results.append({
            "ward_id": ward.id,
            "peak_pollution_hour": "18:00",
            "weekly_trend": random.choice(["rising", "falling", "stable"])
        })
    return results

def get_city_score(db: Session):
    """
    Feature 10: Smart City Pollution Score
    Aggregate city health.
    """
    readings = db.query(AQIReading).order_by(AQIReading.timestamp.desc()).limit(20).all()
    if not readings: return {"city_score": 100, "rating": "Good"}
    
    avg_aqi = sum(r.aqi_value for r in readings) / len(readings)
    # City score (0-100 inverted, where 100 is cleanest)
    score = max(0, 100 - (avg_aqi / 400 * 100))
    
    rating = "Good"
    if score < 40: rating = "Severe Pollution"
    elif score < 60: rating = "High Pollution"
    elif score < 80: rating = "Moderate Pollution"
    
    return {
        "city_score": round(score, 2),
        "rating": rating
    }
