Hyper-Local AQI & Pollution Mitigation Dashboard

An AI-powered smart city pollution intelligence platform that monitors air quality at the ward level, detects pollution sources using AI models, predicts AQI trends, and generates automated mitigation recommendations for city administrators and citizens.

Most air quality systems provide only city-level averages, which hide local pollution hotspots such as construction zones, heavy traffic corridors, or biomass burning areas.

This project builds a hyper-local air pollution monitoring and response system capable of detecting pollution events, predicting trends, and recommending mitigation strategies in real time.

The platform combines geospatial visualization, machine learning, traffic simulation, and real-time dashboards to create a smart city pollution command center.

Project Overview

The system collects simulated traffic data and pollution signals, analyzes their impact on air quality, and presents insights through an interactive dashboard.

City administrators can:

detect pollution hotspots

analyze pollution sources

forecast pollution spikes

deploy mitigation strategies

Citizens can receive real-time health advisories based on pollution levels in their area.

Key Features
Hyper-Local AQI Monitoring

Displays ward-level air quality insights instead of city-wide averages.

AI Pollution Source Detection

Detects common pollution sources such as:

construction dust

traffic emissions

biomass burning

industrial smoke

Traffic Emission Simulation

Simulates vehicle density and traffic congestion to estimate pollution contributions.

Interactive Smart City Dashboard

A command-center style interface showing:

AQI heatmaps

pollution hotspots

traffic emission trends

mitigation recommendations

Pollution Hotspot Detection

Automatically detects wards experiencing abnormal AQI spikes.

AQI Prediction Engine

Forecasts air quality levels for the next 1–3 hours.

Mitigation Recommendation Engine

Suggests actions such as:

traffic diversion

construction regulation

vehicle restrictions

emergency alerts

Citizen Health Advisory System

Provides safety recommendations based on pollution exposure risk.

Pollution Spread Simulation

Predicts how pollution may propagate across city wards.

Environmental Analytics

Provides insights including:

pollution ranking

peak pollution hours

city environmental score

System Workflow

Below is the simplified workflow of the platform.

Traffic Simulation
        │
        ▼
Vehicle Data Extraction
        │
        ▼
Pollution Source Detection
        │
        ▼
AQI Calculation Engine
        │
        ▼
Pollution Hotspot Detection
        │
        ▼
Mitigation Recommendation Engine
        │
        ▼
AQI Prediction Model
        │
        ▼
Real-Time Dashboard Visualization
System Architecture

The system follows a modular smart city architecture where each component processes environmental data and feeds it to the next stage.

               +-------------------+
               |  Traffic Simulator |
               +---------+---------+
                         |
                         ▼
               +-------------------+
               | Vehicle Data Layer |
               +---------+---------+
                         |
                         ▼
              +--------------------+
              | Pollution Detection |
              |   (AI Simulation)   |
              +---------+----------+
                        |
                        ▼
               +-------------------+
               | AQI Engine        |
               | Ward-level AQI    |
               +---------+---------+
                         |
                         ▼
               +-------------------+
               | Mitigation Engine |
               +---------+---------+
                         |
                         ▼
               +-------------------+
               | Prediction Module |
               +---------+---------+
                         |
                         ▼
             +-----------------------+
             | Smart City Dashboard  |
             | React + MapLibre UI   |
             +-----------------------+
Tech Stack
Frontend

React
Tailwind CSS
MapLibre GL (geospatial visualization)
Recharts (data visualization)

Backend

FastAPI
WebSockets for real-time data updates

Database

PostgreSQL
PostGIS for geospatial data

AI / Machine Learning

YOLOv8 (pollution detection simulation)
Scikit-learn (AQI prediction models)

Simulation & Optimization

SUMO (traffic simulation concept)
NetworkX (traffic route optimization)

Data Processing

NumPy
Pandas

Project Modules

The system is divided into multiple modules.

Dashboard

Real-time command center showing pollution insights and analytics.

Pollution Source Analysis

Analyzes and categorizes pollution sources detected across wards.

Traffic Simulation

Simulates vehicle density and traffic flow affecting emissions.

AQI Prediction

Forecasts pollution levels for upcoming hours.

Policy Engine

Recommends mitigation actions for city authorities.

Citizen Health Advisory

Provides pollution exposure warnings and health guidance.

Environmental Analytics

Advanced analytics for pollution trends and city environmental performance.

Screenshots

Add screenshots of the dashboard UI here.

Example structure:

/screenshots/dashboard.png
/screenshots/heatmap.png
/screenshots/prediction.png
/screenshots/policy-engine.png

Example markdown:

## Dashboard
![Dashboard](screenshots/dashboard.png)

## Pollution Heatmap
![Heatmap](screenshots/heatmap.png)

## AQI Prediction
![Prediction](screenshots/prediction.png)
Demo

You can add a demo video or animated GIF showing the system in action.

Example:

/demo/demo.gif

Example markdown:

## Demo

![Demo](demo/demo.gif)

Or provide a video link.

Use Cases

Urban Pollution Monitoring
Smart City Command Centers
Environmental Research
Public Health Monitoring
Urban Policy Decision Support

Future Improvements

Integration with real air quality sensor networks
Satellite pollution monitoring integration
Drone-based pollution surveillance
Deep learning models for improved AQI prediction
Mobile applications for citizen alerts

Contributors

Team Binary

Bhavya Porwal
Yashika Titoria
Apurva Yadav
Vaibhav Sharma

