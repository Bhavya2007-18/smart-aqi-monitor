from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
# Removed geoalchemy2 for SQLite fallback
# from geoalchemy2 import Geometry
from .database import Base
from datetime import datetime

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Falling back to lat/lon for SQLite
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    population_density = Column(Float, nullable=True) # residents per sq km
    
    aqi_readings = relationship("AQIReading", back_populates="ward")
    pollution_sources = relationship("PollutionSource", back_populates="ward")
    traffic_data = relationship("TrafficData", back_populates="ward")
    mitigations = relationship("MitigationAction", back_populates="ward")

class AQIReading(Base):
    __tablename__ = "aqi_readings"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"))
    aqi_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ward = relationship("Ward", back_populates="aqi_readings")

class PollutionSource(Base):
    __tablename__ = "pollution_sources"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"))
    source_type = Column(String) # construction_dust, vehicle_smoke, biomass_burning, industrial_emissions
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ward = relationship("Ward", back_populates="pollution_sources")

class TrafficData(Base):
    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"))
    vehicle_count = Column(Integer)
    average_speed = Column(Float)
    traffic_density = Column(Float)
    emission_index = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ward = relationship("Ward", back_populates="traffic_data")

class MitigationAction(Base):
    __tablename__ = "mitigation_actions"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"))
    action_type = Column(String) # divert traffic, halt construction, etc.
    status = Column(String) # active, resolved
    timestamp = Column(DateTime, default=datetime.utcnow)

    ward = relationship("Ward", back_populates="mitigations")
