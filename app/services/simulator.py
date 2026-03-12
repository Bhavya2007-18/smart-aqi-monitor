from sqlalchemy.orm import Session
from app.models import Ward, MitigationAction, AQIReading
import random

def simulate_mitigation_impact(db: Session, ward_id: int, action: str):
    """
    Feature 5: Smart Mitigation Simulator
    Simulate impact of mitigation strategies on AQI.
    """
    # Base impact values
    impacts = {
        "traffic_diversion": 25,
        "construction_halt": 40,
        "vehicle_restriction": 15,
        "water_sprinklers": 20
    }
    
    reduction = impacts.get(action, 10) + random.uniform(-5, 5)
    
    return {
        "action": action,
        "expected_aqi_reduction": round(reduction, 2),
        "time_to_effect": f"{random.randint(15, 60)} minutes"
    }
