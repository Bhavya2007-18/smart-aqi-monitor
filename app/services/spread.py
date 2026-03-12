from sqlalchemy.orm import Session
from ..models import Ward
import random

def predict_pollution_spread(db: Session):
    """
    Feature 7: Pollution Spread Predictor
    Simulate how pollution moves between wards.
    """
    wards = db.query(Ward).all()
    if not wards or len(wards) < 2:
        return []

    spread_results = []
    for ward in wards:
        # Simplified: pick 1-2 random adjacent wards
        others = [w.id for w in wards if w.id != ward.id]
        affected = random.sample(others, min(len(others), random.randint(1, 3)))
        
        spread_results.append({
            "source_ward": ward.id,
            "affected_wards_next_hour": affected
        })
    return spread_results
