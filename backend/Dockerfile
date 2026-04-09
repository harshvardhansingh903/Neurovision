FROM python:3.11-slim

WORKDIR /app

# Disable OpenCV GUI support (headless environment)
ENV DISPLAY=
ENV QT_QPA_PLATFORM=offscreen

# Install system dependencies for OpenCV (headless mode)
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Copy pre-trained models
COPY models ./models

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
