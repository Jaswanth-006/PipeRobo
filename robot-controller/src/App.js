import React, { useEffect, useState, useRef, useCallback } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState("DISCONNECTED");
  const [frontAngle, setFrontAngle] = useState(90);
  const [backAngle, setBackAngle] = useState(90);
  const ws = useRef(null);
  
  // CONFIG - Make sure this is your current Pi IP
  const PI_IP = "10.118.60.82"; 
  const WS_URL = `ws://${PI_IP}:8000/ws`;
  const VIDEO_URL = `http://${PI_IP}:5000/video_feed`;

  const connectWebSocket = useCallback(() => {
    ws.current = new WebSocket(WS_URL);
    ws.current.onopen = () => setStatus("ONLINE");
    ws.current.onclose = () => { setStatus("OFFLINE"); setTimeout(connectWebSocket, 2000); };
    ws.current.onerror = () => ws.current.close();
  }, [WS_URL]);

  useEffect(() => {
    connectWebSocket();
    return () => { if (ws.current) ws.current.close(); };
  }, [connectWebSocket]);

  const send = (cmd) => {
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(cmd);
  };

  const btnProps = (cmdStart, cmdStop) => ({
    onMouseDown: () => send(cmdStart),
    onMouseUp: () => send(cmdStop),
    onTouchStart: (e) => { e.preventDefault(); send(cmdStart); },
    onTouchEnd: (e) => { e.preventDefault(); send(cmdStop); }
  });

  const updateServo = (type, val) => {
    if (type === 'F') { setFrontAngle(val); send(`S_F${val}`); }
    if (type === 'B') { setBackAngle(val); send(`S_B${val}`); }
  };

    return (
    <div className="dashboard">
      <div className="interface">
        
        {/* LEFT: FRONT DRIVE & SERVO */}
        <div className="control-column">
          <div className="label">FRONT DRIVE</div>
          <div className="btn-group">
            <button className="neon-btn" {...btnProps('F_FWD', 'F_STOP')}>▲</button>
            <button className="neon-btn" {...btnProps('F_BWD', 'F_STOP')}>▼</button>
          </div>
          
          <div className="label mt">FRONT ARM</div>
          <input type="range" className="neon-slider" min="0" max="180" value={frontAngle} 
            onChange={(e) => updateServo('F', e.target.value)} />
          <div className="angle-text">{frontAngle}°</div>
        </div>

        {/* CENTER: STATUS, VIDEO SCREEN & STOP */}
        <div className="center-column">
          <div className={`status ${status}`}>{status}</div>
          
          {/* NEW: DEDICATED VIDEO SCREEN */}
          <div className="video-screen">
            <img src={VIDEO_URL} alt="Waiting for AI Camera..." />
          </div>

          <button className="stop-btn" onClick={() => send('X')}>STOP ALL</button>
        </div>

        {/* RIGHT: BACK DRIVE & SERVO */}
        <div className="control-column">
          <div className="label">BACK DRIVE</div>
          <div className="btn-group">
            <button className="neon-btn" {...btnProps('B_FWD', 'B_STOP')}>▲</button>
            <button className="neon-btn" {...btnProps('B_BWD', 'B_STOP')}>▼</button>
          </div>

          <div className="label mt">BACK ARM</div>
          <input type="range" className="neon-slider" min="0" max="180" value={backAngle} 
            onChange={(e) => updateServo('B', e.target.value)} />
          <div className="angle-text">{backAngle}°</div>
        </div>

      </div>
    </div>
  );
}

export default App;