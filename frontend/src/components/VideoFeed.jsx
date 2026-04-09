import React, { useEffect, useRef } from 'react';

/**
 * VideoFeed Component
 * Captures video from webcam and sends frames to backend.
 * Shows detected emotion, fatigue, and stress in real-time.
 */
const VideoFeed = ({ onFrameCapture, analysisResult = {} }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  // Setup webcam
  useEffect(() => {
    const startWebcam = async () => {
      try {
        // Request camera with decent resolution
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error('Camera access denied:', error);
        alert('Cannot access camera - check permissions');
      }
    };

    startWebcam();

    // Cleanup - stop camera when done
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Capture frames and send to backend
  useEffect(() => {
    const captureFrame = () => {
      if (videoRef.current && canvasRef.current) {
        const ctx = canvasRef.current.getContext('2d');
        
        // Draw current video frame onto canvas
        ctx.drawImage(
          videoRef.current,
          0,
          0,
          canvasRef.current.width,
          canvasRef.current.height
        );

        // Convert to base64 PNG
        const frameData = canvasRef.current.toDataURL('image/png');
        
        // Send frame to parent
        if (onFrameCapture) {
          onFrameCapture(frameData);
        }
      }
    };

    // Capture every 200ms (5 fps)
    intervalRef.current = setInterval(captureFrame, 200);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [onFrameCapture]);

  const emotion = analysisResult.emotion || 'Detecting...';
  const emotionConfidence = analysisResult.emotion_confidence || 0;
  const fatigueScore = analysisResult.fatigue_score || 0;
  const stressLevel = analysisResult.stress_level || 'LOW';

  // Map emotions to colors
  const getEmotionColor = (emotion) => {
    const colorMap = {
      'Happy': '#10b981',
      'Neutral': '#06b6d4',
      'Sad': '#3b82f6',
      'Angry': '#ef4444',
      'Fear': '#8b5cf6',
      'Disgust': '#ec4899',
      'Surprise': '#f59e0b',
      'Unknown': '#6b7280'
    };
    return colorMap[emotion] || colorMap['Unknown'];
  };

  // Color for stress indicator
  const getStressColor = (level) => {
    const colorMap = {
      'LOW': '#10b981',
      'MEDIUM': '#f59e0b',
      'HIGH': '#ef4444'
    };
    return colorMap[level] || colorMap['LOW'];
  };

  const emotionColor = getEmotionColor(emotion);
  const stressColor = getStressColor(stressLevel);

  return (
    <div className="relative w-full h-full bg-navy-lighter rounded-lg overflow-hidden border-2 border-cyan border-opacity-30">
      {/* Hidden canvas for frame capture */}
      <canvas
        ref={canvasRef}
        width={1280}
        height={720}
        className="hidden"
      />

      {/* Video Feed */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />

      {/* Connection Status */}
      <div className="absolute top-4 left-4">
        <div className={`px-4 py-2 rounded-full text-sm font-medium backdrop-blur-md ${
          analysisResult.success 
            ? 'bg-green-500 bg-opacity-20 text-green-300' 
            : 'bg-yellow-500 bg-opacity-20 text-yellow-300'
        }`}>
          {analysisResult.success ? '✓ Analyzing' : '○ Initializing'}
        </div>
      </div>

      {/* Emotion Badge */}
      <div className="absolute top-4 right-4">
        <div 
          className="px-4 py-3 rounded-lg backdrop-blur-md border border-opacity-30"
          style={{
            backgroundColor: `${emotionColor}33`,
            borderColor: emotionColor
          }}
        >
          <div className="text-xs text-gray-400 mb-1">Emotion</div>
          <div 
            className="text-lg font-bold"
            style={{ color: emotionColor }}
          >
            {emotion}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {(emotionConfidence * 100).toFixed(0)}% confidence
          </div>
        </div>
      </div>

      {/* Fatigue Score Bar */}
      <div className="absolute bottom-4 left-4 w-48">
        <div className="text-xs text-gray-400 mb-2">Fatigue Level</div>
        <div className="w-full h-3 bg-navy-lighter rounded-full border border-cyan border-opacity-20 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              fatigueScore < 30 
                ? 'bg-green-500' 
                : fatigueScore < 60 
                ? 'bg-yellow-500' 
                : 'bg-red-500'
            }`}
            style={{ width: `${Math.min(fatigueScore, 100)}%` }}
          />
        </div>
        <div className="text-xs text-gray-300 mt-1">
          {fatigueScore.toFixed(0)}/100
        </div>
      </div>

      {/* Stress Level Badge */}
      <div className="absolute bottom-4 right-4">
        <div className="text-xs text-gray-400 mb-2">Stress Level</div>
        <div 
          className="px-4 py-2 rounded-lg backdrop-blur-md border"
          style={{
            backgroundColor: `${stressColor}33`,
            borderColor: stressColor
          }}
        >
          <div 
            className="text-sm font-bold"
            style={{ color: stressColor }}
          >
            {stressLevel}
          </div>
        </div>
      </div>

      {/* Face Detection Box */}
      {analysisResult.faces_count > 0 && analysisResult.face_rectangle && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <svg className="w-full h-full" style={{ top: 0, left: 0 }}>
            <rect
              x={analysisResult.face_rectangle.x}
              y={analysisResult.face_rectangle.y}
              width={analysisResult.face_rectangle.w}
              height={analysisResult.face_rectangle.h}
              fill="none"
              stroke="#00d9ff"
              strokeWidth="2"
              opacity="0.6"
            />
          </svg>
        </div>
      )}

      {/* No Face Detected */}
      {analysisResult.success && analysisResult.faces_count === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 backdrop-blur-sm">
          <div className="text-center">
            <div className="text-xl text-yellow-400">No Face Detected</div>
            <div className="text-sm text-gray-400 mt-2">Please position your face in the camera</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoFeed;
