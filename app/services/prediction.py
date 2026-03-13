import logging
from sqlalchemy.orm import Session
from app.models import AQIReading

logger = logging.getLogger("prediction_engine")
logging.basicConfig(level=logging.INFO)

def predict_aqi(db: Session):
    """
    Lightweight statistical prediction engine using moving-average and trend-based algorithm.
    Runs efficiently in serverless environments without heavy ML libraries.
    """
    # Fetch historical readings to calculate moving average and trends
    # Fetching the last 60 readings (approx a few hours of data depending on tick rate)
    readings = db.query(AQIReading).order_by(AQIReading.timestamp.desc()).limit(60).all()
    
    if not readings:
        logger.warning("No historical AQI data found for predictions.")
        return {
            "current_aqi": 50,
            "trend": "stable",
            "prediction_6h": 50,
            "prediction_24h": 50
        }
        
    # Calculate current average AQI from the most recent readings (e.g. latest 10)
    recent_readings = readings[:10]
    current_aqi = sum(r.aqi_value for r in recent_readings) / len(recent_readings)
    
    # Compare with older readings to establish a baseline for trend
    older_readings = readings[-10:] if len(readings) >= 20 else readings
    older_aqi = sum(r.aqi_value for r in older_readings) / len(older_readings)
    
    # Calculate trend delta
    delta = current_aqi - older_aqi
    
    if delta > 5:
        trend = "worsening"
        hourly_change = delta / max(1, (len(readings) / 10)) # Rough approximation of hourly drift
    elif delta < -5:
        trend = "improving"
        hourly_change = delta / max(1, (len(readings) / 10))
    else:
        trend = "stable"
        hourly_change = 0
        
    # Bound the hourly trajectory variance to prevent wild runaway numbers
    hourly_change = max(-10.0, min(10.0, hourly_change))
    
    if trend == "stable":
        # Add slight natural fluctuation
        prediction_6h = current_aqi + 2
        prediction_24h = current_aqi - 1
    else:
        prediction_6h = current_aqi + (hourly_change * 6)
        # 24h prediction typically reverts slightly towards mean in real-world diurnal cycles
        mean_reversion = 0.5 
        prediction_24h = current_aqi + (hourly_change * 24 * mean_reversion)
        
    # Cap predictions between valid AQI bounds (0 - 500)
    prediction_6h = max(0.0, min(500.0, prediction_6h))
    prediction_24h = max(0.0, min(500.0, prediction_24h))
    
    result = {
        "current_aqi": round(current_aqi),
        "trend": trend,
        "prediction_6h": round(prediction_6h),
        "prediction_24h": round(prediction_24h)
    }
    
    logger.info(f"Statistical Prediction Computed: {result}")
    
    return result
