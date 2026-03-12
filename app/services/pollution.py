from sqlalchemy.orm import Session
from ..models import Ward, PollutionSource
import random

SOURCES = [
    "construction_dust",
    "vehicle_smoke",
    "biomass_burning",
    "industrial_emissions"
]

def simulate_pollution_detections(db: Session):
    """
    Simulates YOLOv8 detection outputs for pollution sources across wards.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_detections = []
    # Not every ward has a detection every cycle
    for ward in wards:
        if random.random() > 0.7:  # 30% chance to detect a source
            source = random.choice(SOURCES)
            confidence = random.uniform(0.75, 0.99)
            
            ps = PollutionSource(
                ward_id=ward.id,
                source_type=source,
                confidence=round(confidence, 2)
            )
            db.add(ps)
            new_detections.append(ps)
    
    db.commit()
    for ps in new_detections:
        db.refresh(ps)
    
    return new_detections
