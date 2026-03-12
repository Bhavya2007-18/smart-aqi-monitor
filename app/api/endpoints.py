from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Ward, AQIReading, TrafficData, PollutionSource, MitigationAction
from ..schemas import (
    WardResponse, AQIReadingResponse, TrafficDataResponse, PSourceResponse, 
    MitigationActionResponse, AQIPrediction, HotspotResponse, PollutionEvent,
    HealthRiskResponse, SourceProbabilityResponse, MitigationSimulationRequest,
    MitigationSimulationResponse, WardRanking, PollutionSpreadResponse,
    EmergencyStatusResponse, TrendIntelligenceResponse, CityScoreResponse
)
from ..services.prediction import predict_aqi
from ..services.routing import optimize_routes
from ..services import analytics, spread, simulator

router = APIRouter()

# ... existing endpoints ...

@router.get("/hotspots", response_model=list[HotspotResponse])
def get_hotspots(db: Session = Depends(get_db)):
    return analytics.get_hotspots(db)

@router.get("/events", response_model=list[PollutionEvent])
def get_pollution_events(db: Session = Depends(get_db)):
    return analytics.get_pollution_events(db)

@router.get("/health-risk", response_model=list[HealthRiskResponse])
def get_health_risks(db: Session = Depends(get_db)):
    return analytics.get_health_risks(db)

@router.get("/source-analysis", response_model=list[SourceProbabilityResponse])
def get_source_analysis(db: Session = Depends(get_db)):
    return analytics.get_source_probability(db)

@router.post("/simulate-mitigation", response_model=MitigationSimulationResponse)
def simulate_mitigation(req: MitigationSimulationRequest, db: Session = Depends(get_db)):
    return simulator.simulate_mitigation_impact(db, req.ward_id, req.action)

@router.get("/pollution-ranking", response_model=list[WardRanking])
def get_pollution_ranking(db: Session = Depends(get_db)):
    return analytics.get_pollution_ranking(db)

@router.get("/pollution-spread", response_model=list[PollutionSpreadResponse])
def get_pollution_spread(db: Session = Depends(get_db)):
    return spread.predict_pollution_spread(db)

@router.get("/emergency-status", response_model=list[EmergencyStatusResponse])
def get_emergency_status(db: Session = Depends(get_db)):
    return analytics.get_emergency_status(db)

@router.get("/trends", response_model=list[TrendIntelligenceResponse])
def get_trends(db: Session = Depends(get_db)):
    return analytics.get_trends(db)

@router.get("/city-score", response_model=CityScoreResponse)
def get_city_score(db: Session = Depends(get_db)):
    return analytics.get_city_score(db)

@router.get("/wards", response_model=list[WardResponse])
def get_wards(db: Session = Depends(get_db)):
    return db.query(Ward).all()

@router.get("/aqi", response_model=list[AQIReadingResponse])
def get_latest_aqi(db: Session = Depends(get_db)):
    # Get the latest AQI reading for each ward
    wards = db.query(Ward).all()
    results = []
    for w in wards:
        latest = db.query(AQIReading).filter(AQIReading.ward_id == w.id).order_by(AQIReading.timestamp.desc()).first()
        if latest:
            results.append(latest)
    return results

@router.get("/traffic", response_model=list[TrafficDataResponse])
def get_latest_traffic(db: Session = Depends(get_db)):
    wards = db.query(Ward).all()
    results = []
    for w in wards:
        latest = db.query(TrafficData).filter(TrafficData.ward_id == w.id).order_by(TrafficData.timestamp.desc()).first()
        if latest:
            results.append(latest)
    return results

@router.get("/pollution-sources", response_model=list[PSourceResponse])
def get_active_pollution_sources(db: Session = Depends(get_db)):
    # Return sources detected in the last hour? For simplicity, returning latest 50
    return db.query(PollutionSource).order_by(PollutionSource.timestamp.desc()).limit(50).all()

@router.get("/mitigation", response_model=list[MitigationActionResponse])
def get_active_mitigations(db: Session = Depends(get_db)):
    return db.query(MitigationAction).filter(MitigationAction.status == "active").all()

@router.get("/predictions")
def get_aqi_predictions(db: Session = Depends(get_db)):
    # Calls the prediction simulation
    return predict_aqi(db)

@router.get("/routing")
def get_optimal_routes(db: Session = Depends(get_db)):
    # Calls the NetworkX routing optimizer
    return optimize_routes(db)
