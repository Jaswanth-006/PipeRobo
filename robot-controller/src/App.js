import React, { useEffect, useState, useRef, useCallback } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState("Disconnected");
  const [frontAngle, setFrontAngle] = useState(90);
  const [backAngle, setBackAngle] = useState(90);
  const ws = useRef(null);
  
  // REPLACE WITH YOUR PI IP
  const PI_IP = "10.148.173.83"; 
  const WS_URL = `ws://${PI_IP}:8000/ws`;

  // Wrap connection logic in useCallback to satisfy the linter
  const connectWebSocket = useCallback(() => {
    ws.current = new WebSocket(WS_URL);
    
    ws.current.onopen = () => setStatus("CONNECTED");
    
    ws.current.onclose = () => {
      setStatus("DISCONNECTED");
      // Retry connection after 2 seconds
      setTimeout(() => {
        // We re-trigger the connect function safely
        connectWebSocket();
      }, 2000); 
    };

    ws.current.onerror = (err) => {
      console.error("Socket Error:", err);
      ws.current.close();
    };
  }, [WS_URL]); // Dependency on URL ensures it only updates if IP changes

  useEffect(() => {
    connectWebSocket();
    return () => { if (ws.current) ws.current.close(); };
  }, [connectWebSocket]); // Now safe to include

  const sendCommand = (cmd) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(cmd);
    }
  };

  const handleSlider = (type, val) => {
    if (type === 'F') { setFrontAngle(val); sendCommand(`F${val}`); }
    if (type === 'B') { setBackAngle(val); sendCommand(`B${val}`); }
  };

  const resetAll = () => {
    setFrontAngle(90); setBackAngle(90);
    sendCommand('X'); sendCommand('F90'); sendCommand('B90');
  };

  return (
    <div className="dashboard">
      {/* HEADER */}
      <div className="header">
        <div className="status-pill" data-status={status}>
          <span className="dot"></span> {status}
        </div>
        <h3>PI-ROBO COMMANDER</h3>
      </div>

      <div className="controller-body">
        
        {/* LEFT: DRIVE PAD */}
        <div className="panel left-panel">
          <div className="d-pad">
            <button className="d-btn up" 
              onMouseDown={() => sendCommand('W')} onMouseUp={() => sendCommand('X')}
              onTouchStart={() => sendCommand('W')} onTouchEnd={() => sendCommand('X')}
            >▲</button>
            <div className="d-middle"></div>
            <button className="d-btn down"
              onMouseDown={() => sendCommand('S')} onMouseUp={() => sendCommand('X')}
              onTouchStart={() => sendCommand('S')} onTouchEnd={() => sendCommand('X')}
            >▼</button>
          </div>
          <div className="label">DRIVE</div>
        </div>

        {/* CENTER: SLIDERS */}
        <div className="panel center-panel">
          
          <div className="slider-group">
            <div className="slider-header">
              <span>HEAD ROTATION</span>
              <span className="val">{frontAngle}°</span>
            </div>
            <input type="range" min="0" max="180" value={frontAngle}
              onChange={(e) => handleSlider('F', e.target.value)} 
            />
          </div>

          <div className="slider-group">
            <div className="slider-header">
              <span>TAIL ARTICULATION</span>
              <span className="val">{backAngle}°</span>
            </div>
            <input type="range" min="0" max="180" value={backAngle}
              onChange={(e) => handleSlider('B', e.target.value)} 
            />
          </div>

        </div>

        {/* RIGHT: ACTIONS */}
        <div className="panel right-panel">
          <button className="action-btn stop-btn" onClick={() => sendCommand('X')}>
            <span>✖</span>
          </button>
          <button className="action-btn reset-btn" onClick={resetAll}>
            <span>RESET</span>
          </button>
          <div className="label">ACTIONS</div>
        </div>

      </div>
    </div>
  );
}

export default App;