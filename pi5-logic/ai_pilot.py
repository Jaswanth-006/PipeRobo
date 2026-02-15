import cv2
from ultralytics import YOLO
import websocket
import threading
import time
from flask import Flask, Response

# --- CONFIGURATION ---
MODEL_PATH = "best.pt"       # Your custom trained model
CAMERA_ID = 0                # 0 for USB Webcam
CONFIDENCE_THRESHOLD = 0.5 
TARGET_CLASS = "crack"       # Change this to "crack" when using your custom model
SERVER_URL = "ws://localhost:8000/ws"
HTTP_PORT = 5000             # Port for video stream

# --- GLOBAL VARIABLES ---
outputFrame = None
lock = threading.Lock()      # Thread lock for thread-safe image exchange
robot_stopped = False
stop_cooldown = 0 

# --- FLASK APP ---
app = Flask(__name__)

# --- WEBSOCKET CONNECTION ---
ws = None

def on_open(ws):
    print("✅ Connected to Motor Server")

def connect_ws():
    global ws
    ws = websocket.WebSocketApp(SERVER_URL, on_open=on_open)
    ws.run_forever()

# Start WebSocket in background
ws_thread = threading.Thread(target=connect_ws)
ws_thread.daemon = True
ws_thread.start()

def send_stop():
    global robot_stopped, stop_cooldown
    current_time = time.time()
    
    if ws and ws.sock and ws.sock.connected:
        if not robot_stopped or (current_time - stop_cooldown > 2.0):
            print("🚨 DEFECT DETECTED! STOPPING ROBOT! 🚨")
            ws.send("X") 
            robot_stopped = True
            stop_cooldown = current_time

# --- VISION THREAD ---
def vision_loop():
    global outputFrame, robot_stopped, lock
    
    print(f"🧠 Loading Brain: {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)
    
    print("📷 Starting Camera...")
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(3, 640) 
    cap.set(4, 480)

    if not cap.isOpened():
        print("❌ Error: Camera not found!")
        return

    print("👀 AI Pilot Active. Background processing started.")

    while True:
        ret, frame = cap.read()
        if not ret: continue

        # 1. Run Inference
        results = model(frame, stream=True, verbose=False)
        defect_detected = False

        # 2. Draw Boxes
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = model.names[cls_id] 

                if conf > CONFIDENCE_THRESHOLD:
                    defect_detected = True
                    # Draw Bounding Box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = (0, 0, 255) # Red for defect
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 3. Control Logic
        if defect_detected:
            send_stop()
        else:
            if robot_stopped:
                robot_stopped = False 

        # 4. Update Global Frame (Thread Safe)
        with lock:
            outputFrame = frame.copy()

# --- WEB STREAMING GEN ---
def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                continue
            # Encode frame as JPEG
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        
        # Yield the output frame in byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
              bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# --- MAIN ---
if __name__ == "__main__":
    # Start Vision in a separate thread
    t = threading.Thread(target=vision_loop)
    t.daemon = True
    t.start()

    # Start Web Server
    print(f"📡 Video Stream available at http://<PI_IP>:{HTTP_PORT}/video_feed")
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False, threaded=True, use_reloader=False)