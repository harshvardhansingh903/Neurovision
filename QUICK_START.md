# Quick Start Guide for NeuroVision

## 🚀 Get Started in 5 Minutes

### Option 1: Docker Compose (Recommended for beginners)

```bash
# Clone and navigate to project
cd neurovision

# Run everything with Docker
docker-compose up

# Wait for services to initialize (30-60 seconds)
# Open http://localhost:3000 in your browser
```

**That's it!** The app will be running with:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: PostgreSQL on localhost:5432

### Option 2: Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 12+

#### Terminal 1: Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)

# Install dependencies
pip install -r requirements.txt

# Start server
cd app
uvicorn main:app --reload
```

Backend ready at: **http://localhost:8000**

#### Terminal 2: Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend ready at: **http://localhost:3000**

#### Terminal 3: Database (if not using Docker)

```bash
# Create PostgreSQL database
createdb neurovision_db

# Create user (optional)
createuser neurovision
```

## 📸 Using the App

1. **Allow Camera Permission**: Click "Allow" when browser asks for webcam access
2. **Position Your Face**: Center your face in the video feed
3. **Watch Real-Time Analysis**: 
   - Emotion detection updates in top-right corner
   - Fatigue score bar on bottom-left
   - Stress level indicator on bottom-right
4. **Monitor Dashboard**: Check the right panel for:
   - Emotion trends (blue line chart)
   - Fatigue history (orange line chart)
   - Recent alerts log

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| No WebSocket connection | Ensure backend is running on http://localhost:8000 |
| Camera permission denied | Allow camera in browser settings → Privacy |
| "No faces detected" | Improve lighting, position face in center |
| Database connection error | Verify PostgreSQL is running: `psql -U postgres` |
| Port already in use (3000/8000) | Change port numbers or kill process on port |

## 📚 Next Steps

- Read [README.md](./README.md) for full documentation
- Explore API docs at: http://localhost:8000/docs
- Train custom emotion model (see README.md)
- Deploy to production with Docker

## 🎯 Key Features to Try

1. **Emotion Detection**: Make different facial expressions to see real-time classification
2. **Fatigue Alerts**: Close your eyes for 2+ seconds to trigger fatigue alert
3. **Stress Monitoring**: High emotion confidence triggers stress indicators
4. **Historical Charts**: Monitor trends over time in dashboard
5. **Alert History**: Check timestamp and severity of all detected alerts

## 📊 API Testing

Test the API directly:

```bash
# Get API status
curl http://localhost:8000/status

# Get health events
curl http://localhost:8000/api/health-events?minutes=5&limit=10

# Get recent alerts
curl http://localhost:8000/api/alerts

# Get summary statistics
curl http://localhost:8000/api/health-summary?minutes=5
```

## 🐳 Docker Commands

```bash
# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Access database
docker-compose exec db psql -U neurovision -d neurovision_db
```

## 💡 Tips

- **For Best Results**: Use ring light or well-lit room, 60cm away from camera
- **Optimal Frame Rate**: 5 FPS (200ms) balances accuracy and responsiveness
- **Alert Cooldown**: Duplicate alerts suppressed for 10 seconds to reduce spam
- **Dark Mode**: Optimized for low-light environments

---

**Happy analyzing! 🧠✨**

For more details, see the full [README.md](./README.md)
