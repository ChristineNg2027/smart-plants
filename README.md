# Smart Plants — ML-Driven Intelligent Plant Monitoring

An intelligent plant monitoring and watering system that uses machine learning to **predict** soil moisture behavior and automatically optimize watering decisions.

## What It Does

1. Collects real-time soil and environmental data (moisture, temperature, humidity, light)
2. Learns how the plant dries over time using an LSTM neural network
3. Predicts when the plant will become too dry
4. Makes **proactive** watering decisions before drought occurs
5. Continuously improves as new data is collected

The core loop: **Sensor → Model → Decision → Actuator → New Data → Model Update**

---

## Architecture

```
smart-plants/
├── firmware/       # ESP32 — sensors, pump control, WiFi uplink
├── backend/        # FastAPI — ingests readings, stores data, serves predictions
├── scripts/        # PyTorch LSTM — training, prediction, anomaly detection
├── dashboard/      # Streamlit — live monitoring, forecast, watering log
├── data/           # Raw CSVs, processed data, saved model checkpoints
└── infra/          # Docker Compose for backend + dashboard
```

## Stack

| Layer | Technology |
|-------|-----------|
| Microcontroller | ESP32 (ESP-IDF) |
| Backend API | Python + FastAPI + SQLite |
| ML | PyTorch LSTM |
| Dashboard | Python + Streamlit + Plotly |
| Infra | Docker Compose |

## Quick Start

### Firmware
```bash

```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
```

### ML Scripts
```bash
cd scripts
pip install -r requirements.txt
python train.py          # train LSTM on collected data
python predict.py        # run forecast
python evaluate.py       # view metrics and plots
```

### Dashboard
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
# UI available at http://localhost:8501
```

### Docker (backend + dashboard together)
```bash
cd infra
docker-compose up
```

---

## ML

- **Model:** LSTM sequence-to-one regressor
- **Input features:** soil moisture, temperature, humidity, light (sliding window)
- **Output:** predicted moisture level N hours ahead
- **Anomaly detection:** reconstruction error threshold on LSTM encoder

**Drying is modeled as a function of:**
- Light exposure
- Temperature & humidity
- Soil type and pot characteristics
- Past watering events

---

## Hardware

- ESP32S3 development board
- Capacitive soil moisture sensor
- 5V submersible pump + MOSFET driver (e.g. IRLZ44N)
