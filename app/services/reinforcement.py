from sqlalchemy.orm import Session
from app.models import Ward, TrafficData, AQIReading, PollutionSource, MitigationAction

def generate_mitigations(db: Session):
    """
    Simulates an AI decision system (RL-inspired) to recommend mitigations.
    Inputs: traffic density, AQI levels, pollution sources.
    Outputs: mitigation recommendations.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_mitigations = []
    
    for ward in wards:
        aqi = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).first()
        traffic = db.query(TrafficData).filter(TrafficData.ward_id == ward.id).order_by(TrafficData.timestamp.desc()).first()
        sources = db.query(PollutionSource).filter(PollutionSource.ward_id == ward.id).order_by(PollutionSource.timestamp.desc()).limit(3).all()
        
        actions = set()

        # Policy Engine Rules (Simulating RL Output)
        if aqi and aqi.aqi_value > 200:
            actions.add("issue_pollution_alert")
            
            if traffic and traffic.traffic_density > 0.7:
                actions.add("divert_traffic")
                actions.add("restrict_heavy_vehicles")
        
        if aqi and aqi.aqi_value > 300:
            actions.add("halt_construction")
            actions.add("deploy_water_sprinklers")
            
        for s in sources:
            if s.source_type == "construction_dust" and s.confidence > 0.8:
                actions.add("halt_construction")
                actions.add("deploy_water_sprinklers")
            if s.source_type == "vehicle_smoke" and s.confidence > 0.8:
                actions.add("restrict_heavy_vehicles")

        for action in actions:
            # Avoid duplicating active mitigations
            existing = db.query(MitigationAction).filter(
                MitigationAction.ward_id == ward.id, 
                MitigationAction.action_type == action,
                MitigationAction.status == "active"
            ).first()
            if not existing:
                m = MitigationAction(ward_id=ward.id, action_type=action, status="active")
                db.add(m)
                new_mitigations.append(m)

    db.commit()
    for m in new_mitigations:
        db.refresh(m)
        
    return new_mitigations
