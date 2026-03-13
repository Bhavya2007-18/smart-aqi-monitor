try:
    from pydantic import BaseModel, ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel
    PYDANTIC_V2 = False

from datetime import datetime
from typing import Optional, List

# Base schemas
class WardBase(BaseModel):
    name: str

class WardCreate(WardBase):
    pass

class WardResponse(WardBase):
    id: int
    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True

class AQIReadingBase(BaseModel):
    ward_id: int
    aqi_value: float

class AQIReadingResponse(AQIReadingBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class PSourceBase(BaseModel):
    ward_id: int
    source_type: str
    confidence: float

class PSourceResponse(PSourceBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class TrafficDataBase(BaseModel):
    ward_id: int
    vehicle_count: int
    average_speed: float
    traffic_density: float
    emission_index: float

class TrafficDataResponse(TrafficDataBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class MitigationActionBase(BaseModel):
    ward_id: int
    action_type: str
    status: str

class MitigationActionResponse(MitigationActionBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class AQIPrediction(BaseModel):
    ward_id: int
    aqi_1h: float
    aqi_2h: float
    aqi_3h: float

# Phase 2 Schemas

class HotspotResponse(BaseModel):
    ward_id: int
    status: str = "pollution_hotspot"
    severity: str # low, moderate, high
    dominant_source: str

class PollutionEvent(BaseModel):
    event_type: str = "sudden_pollution_spike"
    ward_id: int
    aqi_before: float
    aqi_after: float
    probable_cause: str

class HealthRiskResponse(BaseModel):
    ward_id: int
    risk_level: str # Low Risk, Moderate Risk, High Risk, Severe Risk
    recommended_action: str

class SourceProbabilityResponse(BaseModel):
    ward_id: int
    source_probability: dict # { "traffic_emission": 0.48, ... }

class PollutionSourceDetail(BaseModel):
    type: str # "Vehicle Emissions", "Construction Dust", etc
    probability: float

class PollutionSourceDetectionResponse(BaseModel):
    ward: str
    aqi: float
    sources: List[PollutionSourceDetail]

class MitigationSimulationRequest(BaseModel):
    ward_id: int
    action: str

class MitigationSimulationResponse(BaseModel):
    action: str
    expected_aqi_reduction: float
    time_to_effect: str

class WardRanking(BaseModel):
    rank: int
    ward_id: int
    aqi: float

class PollutionSpreadResponse(BaseModel):
    source_ward: int
    affected_wards_next_hour: List[int]

class EmergencyStatusResponse(BaseModel):
    ward_id: int
    emergency_mode: bool
    actions: List[str]

class TrendIntelligenceResponse(BaseModel):
    ward_id: int
    peak_pollution_hour: str
    weekly_trend: str # rising, falling, stable

class CityScoreResponse(BaseModel):
    city_score: float
    rating: str
