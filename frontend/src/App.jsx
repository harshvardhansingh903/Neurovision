import React, { useState, useCallback } from 'react';
import VideoFeed from './components/VideoFeed';
import AnalysisDashboard from './components/AnalysisDashboard';
import { useWebSocket } from './hooks/useWebSocket';

/**
 * Main App - ties everything together
 * Video feed + analysis dashboard + WebSocket connection
 */
function App() {
  const [analysisResult, setAnalysisResult] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [clientId] = useState(`client-${Date.now()}-${Math.random()}`);

  // Process results from backend
  const handleFrameAnalysis = useCallback((result) => {
    try {
      if (result.success) {
        setAnalysisResult(result);

        // Log any alerts
        if (result.alerts && result.alerts.length > 0) {
          setAlerts(prev => {
            const newAlerts = result.alerts.map(alert => ({
              ...alert,
              receivedAt: Date.now()
            }));
            // Keep recent alerts only (last 20)
            return [...newAlerts, ...prev].slice(0, 20);
          });
        }
      } else {
        setAnalysisResult(result);
      }
    } catch (error) {
      console.error('Error handling results:', error);
    }
  }, []);

  // Connect to backend WebSocket
  const { isConnected, sendFrame } = useWebSocket(clientId, handleFrameAnalysis);

  // Send frames when captured
  const handleFrameCapture = useCallback((frameData) => {
    if (isConnected) {
      sendFrame(frameData);
    }
  }, [isConnected, sendFrame]);

  return (
    <div className="w-screen h-screen bg-navy text-white overflow-hidden">
      
      {/* Header */}
      <header className="bg-gradient-to-r from-navy-light to-navy border-b border-cyan border-opacity-20 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan to-teal">
              NeuroVision
            </h1>
            <p className="text-sm text-gray-400 mt-1">Real-Time AI Health Analyzer</p>
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center space-x-3">
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
              isConnected 
                ? 'bg-green-500 bg-opacity-20 text-green-300 border border-green-500' 
                : 'bg-red-500 bg-opacity-20 text-red-300 border border-red-500'
            }`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} ${isConnected ? 'animate-pulse' : ''}`}></div>
              <span className="text-sm font-medium">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            
            {/* Client ID */}
            <div className="text-xs text-gray-500 px-3 py-2 bg-navy-lighter rounded">
              ID: {clientId.split('-')[0]}...
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="h-[calc(100vh-80px)] overflow-hidden">
        <div className="grid grid-cols-3 gap-4 h-full p-4">
          
          {/* Video Feed - Spans 2 columns */}
          <div className="col-span-2">
            <VideoFeed 
              onFrameCapture={handleFrameCapture}
              analysisResult={analysisResult}
            />
          </div>

          {/* Dashboard - 1 column */}
          <div className="col-span-1">
            <AnalysisDashboard 
              analysisResult={analysisResult}
              alerts={alerts}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 right-0 p-4 text-xs text-gray-600">
        <div>NeuroVision v1.0.0</div>
        <div className="text-gray-700">{analysisResult.frame_id || 0} frames processed</div>
      </footer>
    </div>
  );
}

export default App;
