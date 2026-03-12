from sqlalchemy.orm import Session
from ..models import Ward, TrafficData
import random

def simulate_traffic(db: Session):
    """
    Simulates traffic flow for all wards.
    Generates synthetic data including vehicle_count, average_speed, traffic_density, and emission_index.
    """
    wards = db.query(Ward).all()
    if not wards:
        return []

    new_traffic_data = []
    for ward in wards:
        vehicle_count = random.randint(50, 500)
        # Higher density implies lower speed
        traffic_density = vehicle_count / 500.0
        average_speed = max(10, 60 - (traffic_density * 50)) + random.uniform(-5, 5)
        # Emission index correlates with density and inversely with speed
        emission_index = (vehicle_count * 0.1) + (60 / average_speed * 10) + random.uniform(0, 10)

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
