import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

/**
 * Dashboard showing real-time metrics and charts.
 * Displays emotion trends, fatigue level, stress, and alerts.
 */
const AnalysisDashboard = ({ analysisResult = {}, alerts = [] }) => {
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [fatigueHistory, setFatigueHistory] = useState([]);

  // Track emotion changes over time
  useEffect(() => {
    if (analysisResult.success && analysisResult.emotion) {
      setEmotionHistory(prev => {
        const newEntry = {
          time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          emotion: analysisResult.emotion,
          confidence: analysisResult.emotion_confidence,
          timestamp: Date.now()
        };
        
        // Keep last 60 samples
        return [...prev, newEntry].slice(-60);
      });
    }
  }, [analysisResult.emotion, analysisResult.emotion_confidence, analysisResult.success]);

  // Track fatigue over time
  useEffect(() => {
    if (analysisResult.success) {
      setFatigueHistory(prev => {
        const newEntry = {
          time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          fatigue: analysisResult.fatigue_score,
          timestamp: Date.now()
        };
        
        // Keep last 60 samples
        return [...prev, newEntry].slice(-60);
      });
    }
  }, [analysisResult.fatigue_score, analysisResult.success]);

  // Emotion color mapping
  const getEmotionBgColor = (emotion) => {
    const colors = {
      'Happy': 'bg-green-900 border-green-500',
      'Neutral': 'bg-cyan-900 border-cyan-500',
      'Sad': 'bg-blue-900 border-blue-500',
      'Angry': 'bg-red-900 border-red-500',
      'Fear': 'bg-purple-900 border-purple-500',
      'Disgust': 'bg-pink-900 border-pink-500',
      'Surprise': 'bg-yellow-900 border-yellow-500',
      'Unknown': 'bg-gray-900 border-gray-500'
    };
    return colors[emotion] || colors['Unknown'];
  };

  const getEmotionTextColor = (emotion) => {
    const colors = {
      'Happy': 'text-green-300',
      'Neutral': 'text-cyan-300',
      'Sad': 'text-blue-300',
      'Angry': 'text-red-300',
      'Fear': 'text-purple-300',
      'Disgust': 'text-pink-300',
      'Surprise': 'text-yellow-300',
      'Unknown': 'text-gray-300'
    };
    return colors[emotion] || colors['Unknown'];
  };

  // Get colored stress indicator
  const getStressIndicator = (level) => {
    const indicators = {
      'LOW': { color: 'bg-green-500', text: 'text-green-300', label: 'Low' },
      'MEDIUM': { color: 'bg-yellow-500', text: 'text-yellow-300', label: 'Medium' },
      'HIGH': { color: 'bg-red-500', text: 'text-red-300', label: 'High' }
    };
    return indicators[level] || indicators['LOW'];
  };

  const stressIndicator = getStressIndicator(analysisResult.stress_level || 'LOW');

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-navy to-navy-light rounded-lg border border-cyan border-opacity-20 overflow-hidden">
      
      {/* Header */}
      <div className="bg-navy-light bg-opacity-50 border-b border-cyan border-opacity-20 px-6 py-4">
        <h2 className="text-xl font-bold text-cyan">Live Health Dashboard</h2>
        <p className="text-sm text-gray-400 mt-1">Real-time analysis and insights</p>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          
          {/* Current Emotion */}
          <div className={`p-4 rounded-lg border-2 ${getEmotionBgColor(analysisResult.emotion)}`}>
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Current Emotion</div>
            <div className={`text-2xl font-bold ${getEmotionTextColor(analysisResult.emotion)}`}>
              {analysisResult.emotion || 'Detecting'}
            </div>
            <div className="text-xs text-gray-400 mt-2">
              {analysisResult.emotion_confidence ? `${(analysisResult.emotion_confidence * 100).toFixed(0)}% confident` : '---'}
            </div>
          </div>

          {/* Fatigue Score */}
          <div className="p-4 rounded-lg border-2 border-orange-600 bg-orange-900 bg-opacity-20">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Fatigue</div>
            <div className="text-2xl font-bold text-orange-300">
              {analysisResult.fatigue_score ? analysisResult.fatigue_score.toFixed(0) : '-'}
            </div>
            <div className="text-xs text-gray-400 mt-2">/ 100</div>
          </div>

          {/* Stress Level */}
          <div className={`p-4 rounded-lg border-2 border-opacity-50 bg-opacity-20 col-span-2 ${stressIndicator.color} ${stressIndicator.text}`}>
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Stress Level</div>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">{analysisResult.stress_level || 'LOW'}</div>
              <div className={`w-4 h-4 rounded-full ${stressIndicator.color}`}></div>
            </div>
          </div>
        </div>

        {/* Emotion Trend Chart */}
        <div className="bg-navy-lighter bg-opacity-50 rounded-lg border border-cyan border-opacity-20 p-4">
          <h3 className="text-sm font-semibold text-cyan mb-4">Emotion Confidence Trend (60s)</h3>
          {emotionHistory.length > 1 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={emotionHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  interval={Math.max(0, Math.floor(emotionHistory.length / 6))}
                />
                <YAxis 
                  domain={[0, 1]}
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #00d9ff' }}
                  labelStyle={{ color: '#00d9ff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="confidence" 
                  stroke="#00d9ff" 
                  dot={false}
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-gray-500">
              Collecting data...
            </div>
          )}
        </div>

        {/* Fatigue Trend Chart */}
        <div className="bg-navy-lighter bg-opacity-50 rounded-lg border border-cyan border-opacity-20 p-4">
          <h3 className="text-sm font-semibold text-cyan mb-4">Fatigue Score Trend (60s)</h3>
          {fatigueHistory.length > 1 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={fatigueHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  interval={Math.max(0, Math.floor(fatigueHistory.length / 6))}
                />
                <YAxis 
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #00d9ff' }}
                  labelStyle={{ color: '#00d9ff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="fatigue" 
                  stroke="#fbbf24" 
                  dot={false}
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-gray-500">
              Collecting data...
            </div>
          )}
        </div>

        {/* Alerts History */}
        <div className="bg-navy-lighter bg-opacity-50 rounded-lg border border-cyan border-opacity-20 p-4">
          <h3 className="text-sm font-semibold text-cyan mb-4">Alert History</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {alerts.length > 0 ? (
              alerts.map((alert, idx) => (
                <div 
                  key={idx}
                  className={`p-3 rounded text-xs border-l-4 ${
                    alert.type === 'FATIGUE' 
                      ? 'bg-orange-900 bg-opacity-20 border-orange-500 text-orange-300'
                      : alert.type === 'STRESS'
                      ? 'bg-red-900 bg-opacity-20 border-red-500 text-red-300'
                      : 'bg-yellow-900 bg-opacity-20 border-yellow-500 text-yellow-300'
                  }`}
                >
                  <div className="font-medium">[{alert.type}]</div>
                  <div className="text-gray-300 mt-1">{alert.message}</div>
                  <div className="text-gray-500 mt-1 text-xs">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                No alerts yet. Keep healthy! 💚
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDashboard;
