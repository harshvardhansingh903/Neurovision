# NeuroVision

## Real-Time AI-Powered Health Analysis Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square) ![React](https://img.shields.io/badge/React-18.2-61dafb?style=flat-square) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-orange?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-Containerized-2496ed?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

NeuroVision is a comprehensive full-stack application that performs real-time facial analysis to detect emotion, fatigue levels, and stress indicators. Built with modern web technologies and deep learning, it provides intelligent health monitoring through a professional dashboard with live alerts and persistent logging.

---

## Overview

### Key Capabilities

- **Real-Time Facial Analysis** — WebSocket-based streaming analysis at 5 FPS (200ms intervals)
- **Emotion Detection** — 7-class CNN classifier (Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise)
- **Fatigue Monitoring** — Eye closure tracking with blink rate analysis
- **Stress Assessment** — Facial action unit classification with adaptive thresholds
- **Live Alert System** — Intelligent notification engine with cooldown mechanisms
- **Professional Dashboard** — Real-time metric visualization with 60-second history
- **Enterprise Architecture** — PostgreSQL integration for event logging and analytics
- **Containerized Deployment** — Docker support for streamlined deployment

**For detailed technical features, see [FEATURES.md](FEATURES.md) | [Implementation notes](IMPROVEMENTS.md)**

---

## User Interface

The NeuroVision dashboard provides a real-time health analysis interface with live emotion detection, fatigue monitoring, and stress assessment metrics.

![NeuroVision Dashboard](Screenshot%202026-04-09%20220714.png)

**Dashboard Features:**
- Live webcam feed with real-time emotion overlay
- Emotion confidence indicator with 60-second trend history
- Fatigue level gauge and stress indicator
- Alert notification log for health events
- Dark mode professional UI with intuitive control layout

---

## System Architecture

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Environment and application settings
│   │   ├── database/
│   │   │   ├── database.py         # SQLAlchemy ORM configuration
│   │   │   └── models.py           # Data models (HealthEvent, AlertLog)
│   │   ├── models/
│   │   │   ├── emotion_model.py    # CNN architecture definition
│   │   │   └── model_manager.py    # Model lifecycle and inference
│   │   ├── routes/
│   │   │   ├── analysis.py         # REST API endpoints
│   │   │   └── websocket.py        # Real-time streaming endpoint
│   │   └── utils/
│   │       ├── frame_processor.py  # Image processing pipeline
│   │       ├── health_analyzer.py  # Metric calculation engine
│   │       └── alert_manager.py    # Alert generation logic
│   ├── requirements.txt
│   ├── Dockerfile
│   └── train_from_images.py        # Model training script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoFeed.jsx       # Webcam capture and rendering
│   │   │   └── AnalysisDashboard.jsx # Real-time metrics display
│   │   ├── hooks/
│   │   │   └── useWebSocket.js     # WebSocket connection management
│   │   ├── App.jsx                 # Root component
│   │   ├── main.jsx                # Application bootstrap
│   │   └── index.css               # Global styles
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── models/
    └── emotion_model.h5            # Pre-trained model weights
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher
- Modern web browser with WebSocket support

### Backend Configuration

**1. Set up Python environment**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure database**

```bash
# Create PostgreSQL database and user
createdb neurovision_db
createuser neurovision
```

Update `.env` file:
```
DATABASE_URL=postgresql://neurovision:password@localhost:5432/neurovision_db
FRONTEND_URL=http://localhost:3000
DEBUG=True
```

**4. Start backend server**

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### Frontend Configuration

**1. Install dependencies**

```bash
cd frontend
npm install
```

**2. Start development server**

```bash
npm run dev
```

Frontend: `http://localhost:3000`

**3. Production build**

```bash
npm run build
npm run preview
```

---

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up --build
```

This deploys three services:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- React frontend (port 3000)

### Manual Docker Build

```bash
# Backend
cd backend
docker build -t neurovision-backend:latest .
docker run -p 8000:8000 neurovision-backend:latest

# Frontend
cd frontend
docker build -t neurovision-frontend:latest .
docker run -p 3000:3000 neurovision-frontend:latest
```

---

## API Reference

### REST Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health-event` | POST | Log a health analysis event |
| `/api/health-events` | GET | Retrieve historical health events |
| `/api/alerts` | GET | Retrieve alert history |
| `/api/health-summary` | GET | Get aggregated statistics |
| `/api/status` | GET | System status check |
| `/docs` | GET | Interactive API documentation |

**Query Parameters:**
- `minutes` — Time window for data retrieval (default: 5)
- `limit` — Maximum records to return (default: 100)

### WebSocket Endpoint

**Connection:** `WS /ws/stream/{client_id}`

**Client Message:**
```json
{
  "type": "frame",
  "frame": "base64_encoded_image_data",
  "timestamp": 1712700000000
}
```

**Server Response:**
```json
{
  "success": true,
  "emotion": "Happy",
  "emotion_confidence": 0.95,
  "fatigue_score": 25.5,
  "stress_level": "LOW",
  "face_detected": true,
  "alerts": [
    {
      "type": "FATIGUE",
      "message": "High fatigue detected",
      "severity": "warning"
    }
  ]
}
```

---

## Model Architecture

### Emotion Classification CNN

**Input Specification:**
- Dimensions: 48×48 pixels
- Format: Grayscale (single channel)
- Preprocessing: Normalized to [0, 1]

**Architecture:**
- 4 convolutional blocks with batch normalization
- Each block: Conv2D → BatchNorm → Conv2D → BatchNorm → MaxPool2D → Dropout
- Dense layers: 512 → 256 units with dropout
- Output: 7 emotion classes with softmax activation

**Performance:**
- Training accuracy: 69-72% (FER2013 dataset)
- Inference latency: 50-100ms per frame
- Model size: 82.4 MB

### Health Metrics Calculation

**Fatigue Score (0-100 scale)**

Calculated from:
- Eye closure duration (40% weight)
- Blink rate deviation from 15-20 bpm (60% weight)
- Threshold: Eye closure >2000ms triggers fatigue alert

**Stress Level Assessment**

Categories: LOW / MEDIUM / HIGH

Based on:
- Emotion history (negative emotions: Angry, Fear, Sad, Disgust)
- Prediction confidence scores
- Temporal consistency (3-second rolling window)

**Emotion Detection**

- Haar Cascade classifier for face localization
- 48×48 ROI extraction and normalization
- CNN inference with confidence scoring
- Temporal smoothing: 7-frame voting window

---

## Configuration

Core settings in `backend/app/config.py`:

```python
# Analysis Thresholds
FATIGUE_EYE_CLOSURE_THRESHOLD_MS = 2000
FATIGUE_BLINK_RATE_THRESHOLD = 15
STRESS_ACTION_UNIT_THRESHOLD = 0.6
EMOTION_CONFIDENCE_THRESHOLD = 0.7

# System Parameters
FRAME_CAPTURE_INTERVAL_MS = 200
TEMPORAL_SMOOTHING_WINDOW = 7
ALERT_COOLDOWN_SECONDS = 10
```

---

## Training Custom Models

### Using Provided Training Script

```bash
cd backend
python train_from_images.py
```

Dataset structure:
```
archive/processed_data/
├── angry/        (image files)
├── disgust/      (image files)
├── fear/         (image files)
├── happy/        (image files)
├── neutral/      (image files)
├── sad/          (image files)
└── surprise/     (image files)
```

**Training Configuration:**
- Epochs: 150
- Batch size: 32
- Data augmentation: Rotation, shift, zoom, brightness variance
- Validation split: 20%
- Test split: 10%

---

## User Interface Design

### Visual Components

**Emotion Indicators:**
- Happy → Green (#10b981)
- Neutral → Cyan (#06b6d4)
- Sad → Blue (#3b82f6)
- Angry → Red (#ef4444)
- Fear → Purple (#8b5cf6)
- Disgust → Pink (#ec4899)
- Surprise → Yellow (#f59e0b)

**Stress Levels:**
- Low → Green (#10b981)
- Medium → Amber (#f59e0b)
- High → Red (#ef4444)

**Dashboard Components:**
- Real-time emotion trend (60-second history)
- Fatigue level gauge
- Stress indicator
- Alert notification log

---

## Troubleshooting

### WebSocket Connection Failed

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check firewall and port availability
lsof -i :8000  # Linux/macOS
netstat -an | find "8000"  # Windows
```

### Face Detection Issues

- Ensure adequate ambient light (>500 lux recommended)
- Position face centered in camera frame
- Grant camera permissions to browser

### Model Loading Errors

Ensure `models/emotion_model.h5` exists and is readable:
```bash
ls -lh backend/models/emotion_model.h5
```

If missing, train a new model or download pre-trained weights.

### Database Connection Issues

Verify PostgreSQL connectivity:
```bash
psql -h localhost -U neurovision -d neurovision_db
```

Confirm connection string in `.env` file matches your database configuration.

---

## Performance Specifications

| Metric | Value |
|--------|-------|
| Frame Processing Latency | ~200ms |
| Model Inference Time | 50-100ms |
| WebSocket Message Size | 2-5 KB |
| Backend Memory Usage | ~500 MB |
| Frontend Memory Usage | ~300 MB |
| Supported Concurrent Clients | 10+ |

---

## Security Considerations

1. **CORS Policy** — Restricted to configured frontend origin
2. **Host Validation** — Trusted host middleware prevents header injection attacks
3. **Environment Secrets** — Sensitive credentials stored in `.env` file
4. **Database Security** — Use strong passwords and principle of least privilege
5. **WebSocket Authentication** — Implement JWT tokens for production environments

---

## Technology Stack

### Backend
- FastAPI 0.104.1 — Modern async web framework
- TensorFlow 2.14.0 — Machine learning inference
- OpenCV 4.8.1 — Computer vision processing
- SQLAlchemy 2.0.23 — Object-relational mapping
- PostgreSQL 15 — Relational database
- Uvicorn 0.24.0 — ASGI application server

### Frontend
- React 18.2.0 — UI framework
- Recharts 2.10.0 — Data visualization
- Tailwind CSS 3.3.0 — Utility-first styling
- Vite 5.0.0 — Frontend build tool

---

## Development Guidelines

### Adding New Metrics

1. Implement calculation in `backend/app/utils/health_analyzer.py`
2. Add database schema in `backend/app/database/models.py`
3. Update WebSocket response in `backend/app/routes/websocket.py`
4. Add UI component in `frontend/src/components/AnalysisDashboard.jsx`

### Extending Alert System

Modify `backend/app/utils/alert_manager.py`:
- Define new alert conditions
- Set thresholds in `backend/app/config.py`
- Trigger evaluation in streaming pipeline

---

## Project Metrics

| Metric | Value |
|--------|-------|
| Total Lines of Code | ~3,500 |
| React Components | 2 (VideoFeed, Dashboard) |
| Backend Modules | 5 (models, routes, utils, database) |
| Real-Time Detection | 5 FPS @ 200ms intervals |
| Model Accuracy | 69% (7-class emotion) |
| Inference Latency | <100ms on CPU |
| Deployment | Docker Compose (3 containers) |
| Response Time | <200ms |
| Supported Concurrent Clients | 10+ |

---

## Known Limitations & Future Enhancements

### Current Limitations

- Single face detection only (can add multi-face support)
- 69% model accuracy (requires longer training for improvement)
- Requires adequate lighting conditions (>500 lux recommended)
- WebSocket lacks authentication (demo version)
- No user login system

### Future Roadmap

- [ ] Multi-face simultaneous detection and tracking
- [ ] Enhanced emotion model (target: >85% accuracy with 200+ epochs)
- [ ] User authentication and account management
- [ ] JWT-based WebSocket authentication for production
- [ ] Real-time data export (CSV/Excel)
- [ ] Advanced analytics and historical reporting
- [ ] GPU acceleration support (CUDA/cuDNN)
- [ ] API rate limiting and throttling
- [ ] Mobile app companion (React Native)
- [ ] Anxiety/stress prediction models
- [ ] Integration with health platforms (Apple Health, Google Fit)
- [ ] Multi-language UI support

---

## License

MIT License — Commercial and personal use permitted.

---

## Version Information

**Current Version:** 1.0.0  
**Last Updated:** April 2026  
**Status:** Production Ready
