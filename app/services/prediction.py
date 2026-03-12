from sqlalchemy.orm import Session
from app.models import Ward, AQIReading
import datetime
import random

try:
    from sklearn.linear_model import LinearRegression
    import numpy as np
    _HAS_ML = True
except ImportError:
    _HAS_ML = False
    print("ML Libraries not found, using rule-based simulation.")

def predict_aqi(db: Session):
    """
    Predict AQI for 1h, 2h, and 3h using simple linear regression 
    over recent historical data or a rule-based simulation if data is sparse.
    """
    wards = db.query(Ward).all()
    predictions = {}
    
    for ward in wards:
        try:
            # Fetch the last 20 readings (assuming frequent updates)
            readings = db.query(AQIReading).filter(AQIReading.ward_id == ward.id).order_by(AQIReading.timestamp.desc()).limit(20).all()
            
            if not _HAS_ML or len(readings) < 5:
                # Not enough data or missing ML libs, simulate trend
                current_aqi = readings[0].aqi_value if readings else 100
                trend = random.uniform(-10, 20) # Mostly increasing or stabilizing
                predictions[ward.id] = {
                    "aqi_1h": min(400, max(50, current_aqi + trend)),
                    "aqi_2h": min(400, max(50, current_aqi + trend * 1.8)),
                    "aqi_3h": min(400, max(50, current_aqi + trend * 2.5)),
                }
                continue
                
            # Reverse to get chronological order
            readings.reverse()
            
            # Simple X = time index, Y = AQI
            X = np.array(range(len(readings))).reshape(-1, 1)
            y = np.array([r.aqi_value for r in readings])
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict for future indices corresponding to 1h, 2h, 3h 
            future_X = np.array([[len(readings) + 6], [len(readings) + 12], [len(readings) + 18]])
            preds = model.predict(future_X)
            
            predictions[ward.id] = {
                "aqi_1h": round(min(400, max(50, preds[0])), 2),
                "aqi_2h": round(min(400, max(50, preds[1])), 2),
                "aqi_3h": round(min(400, max(50, preds[2])), 2),
            }
        except Exception as e:
            # Catch-all for any math errors during prediction
            print(f"Prediction Error for {ward.name}: {e}")
            predictions[ward.id] = {
                "aqi_1h": random.uniform(80, 150),
                "aqi_2h": random.uniform(85, 160),
                "aqi_3h": random.uniform(90, 170),
            }
            
    return predictions
