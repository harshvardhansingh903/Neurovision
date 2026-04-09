import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Hook for WebSocket connection to the backend.
 * Handles sending frames and getting emotion results back.
 */
export const useWebSocket = (clientId, onFrame) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messageCount, setMessageCount] = useState(0);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = useRef(1000);

  const connect = useCallback(() => {
    try {
      // Figure out if we're in Docker or local dev
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const hostname = window.location.hostname === 'localhost' ? 'localhost' : 'backend';
      const wsUrl = `${protocol}//${hostname}:8000/ws/stream/${clientId}`;
      
      console.log('Connecting to:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('Connected to backend');
        setIsConnected(true);
        reconnectAttempts.current = 0;
        reconnectDelay.current = 1000;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setMessageCount(prev => prev + 1);
          
          if (onFrame) {
            onFrame(data);
          }
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.current.onclose = () => {
        console.log('Disconnected');
        setIsConnected(false);
        // Try to reconnect
        attemptReconnect();
      };
    } catch (error) {
      console.error('Connection failed:', error);
      attemptReconnect();
    }
  }, [clientId, onFrame]);

  const attemptReconnect = useCallback(() => {
    if (reconnectAttempts.current < maxReconnectAttempts) {
      reconnectAttempts.current += 1;
      console.log(`Reconnect attempt ${reconnectAttempts.current}/${maxReconnectAttempts}`);
      setTimeout(() => {
        connect();
      }, reconnectDelay.current);
      // Exponential backoff
      reconnectDelay.current = Math.min(reconnectDelay.current * 2, 10000);
    } else {
      console.error('Could not reconnect - giving up');
    }
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendFrame = (frameData) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(
          JSON.stringify({
            type: 'frame',
            frame: frameData,
            timestamp: Date.now()
          })
        );
      } catch (error) {
        console.error('Failed to send frame:', error);
      }
    }
  };

  const ping = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        })
      );
    }
  };

  return {
    isConnected,
    sendFrame,
    ping,
    messageCount
  };
};
    }
  };

  const ping = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        })
      );
    }
  };

  return {
    isConnected,
    sendFrame,
    ping,
    messageCount
  };
};
