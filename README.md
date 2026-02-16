
# PipeRobo: AI-Powered Pipe Inspection Robot

PipeRobo is an end-to-end system for automated pipe inspection using computer vision and robotics. It combines:
- **AI-based defect detection** (cracks, corrosion) using YOLOv8
- **Raspberry Pi-based robot control** (motors, servos)
- **Web dashboard** for real-time video and remote control

---

## Project Structure

```
PipeRobo/
├── pi5-logic/           # Python code for AI & robot control
│   ├── ai_pilot.py      # AI vision & video streaming
│   ├── robot_server.py  # Motor/servo control server (FastAPI WebSocket)
│   ├── start_robot.py   # Launches both servers together
│   ├── best.pt          # Trained YOLOv8 model
│   ├── data.yaml        # YOLO dataset config
│   ├── convert_data.py  # Data conversion utility
│   └── datasets/        # Training/validation images & labels
├── robot-controller/    # React web dashboard for remote control
│   ├── src/App.js       # Main dashboard UI
│   └── ...
└── README.md            # This file
```

---

## 1. Hardware & Prerequisites

- Raspberry Pi (or compatible Linux SBC)
- PCA9685 PWM driver (for motors/servos)
- Camera (USB or PiCam)
- Python 3.8+
- Node.js (for web dashboard)

---

## 2. Python Environment Setup

Install dependencies (on the Pi):

```bash
cd pi5-logic
pip install -r requirements.txt
# If requirements.txt is missing, install:
pip install ultralytics opencv-python flask fastapi uvicorn adafruit-circuitpython-pca9685 websocket-client
```

---

## 3. Dataset & Training (YOLOv8)

- Images and bounding box labels are in `pi5-logic/datasets/`
- Classes: `crack`, `corrosion`
- To convert Edge Impulse/labelbox data to YOLO format, use `convert_data.py`
- To train a new model:

```bash
# Install ultralytics if not present
pip install ultralytics
# Train (from pi5-logic/):
yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
# Best model will be saved as runs/detect/train/weights/best.pt
```

---

## 4. Running the Robot (AI + Motors)

From `pi5-logic/`:

```bash
python start_robot.py
# This launches both the robot server (motors) and AI pilot (vision)
```

- Motor server runs on port 8000 (WebSocket)
- AI video stream runs on port 5000 (`/video_feed`)

---

## 5. Web Dashboard (Remote Control)

From `robot-controller/`:

```bash
npm install
npm start
# Open http://localhost:3000
```

**Features:**
- Live video from robot
- Drive controls (forward/back, stop)
- Servo arm sliders
- Emergency stop

**Note:** Set the correct Pi IP in `src/App.js` (`PI_IP` variable)

---

## 6. File Overview

- `pi5-logic/ai_pilot.py`: Runs YOLOv8 on camera frames, draws boxes, streams video, sends stop command if defect detected
- `pi5-logic/robot_server.py`: WebSocket server for motor/servo control (W/S/X/Fxx/Bxx commands)
- `pi5-logic/start_robot.py`: Launches both servers, handles shutdown
- `robot-controller/`: React app for remote control and video

---

## 7. Example Workflow

1. **Collect images** of pipes with/without defects
2. **Label images** (Edge Impulse, Labelbox, etc.)
3. **Convert labels** to YOLO format (`convert_data.py`)
4. **Train YOLOv8** model, export `best.pt`
5. **Deploy model** to `pi5-logic/`
6. **Run `start_robot.py`** on the Pi
7. **Control robot** from the web dashboard

---

## 8. Troubleshooting

- **Camera not found:** Check camera connection, try changing `CAMERA_ID` in `ai_pilot.py`
- **No video in dashboard:** Ensure AI pilot is running, check Pi IP in `App.js`
- **Motors not moving:** Check PCA9685 wiring, power, and I2C address
- **WebSocket errors:** Ensure ports 8000 (robot) and 5000 (video) are open

---

## 9. Credits

- Project by [Your Name/Team]
- Built with YOLOv8, FastAPI, Flask, React, PCA9685, and Raspberry Pi

---

## 10. License

MIT License (or specify your own)
