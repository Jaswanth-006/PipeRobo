import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

# --- HARDWARE SETUP ---
try:
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c)
    pca.frequency = 60
except:
    print("Hardware not found! Running in Simulation Mode.")
    pca = None

# --- WIRING CONFIGURATION ---
# Front Motors (Channels 0, 1)
FRONT_IN1 = 0
FRONT_IN2 = 1

# Back Motors (Channels 2, 3)
BACK_IN3 = 2
BACK_IN4 = 3

# Servos
SERVO_FRONT = 15
SERVO_BACK = 14
SERVOMIN, SERVOMAX = 150, 720 

# --- HELPER FUNCTIONS ---
def set_digital(channel, state):
    if pca is None: return
    if state: pca.channels[channel].duty_cycle = 0xFFFF
    else: pca.channels[channel].duty_cycle = 0

def set_servo(channel, angle):
    if pca is None: return
    angle = max(0, min(180, angle))
    pulse = int(SERVOMIN + (angle / 180.0) * (SERVOMAX - SERVOMIN))
    duty = int((pulse / 4096) * 65535)
    pca.channels[channel].duty_cycle = duty

def stop_motors():
    set_digital(FRONT_IN1, False); set_digital(FRONT_IN2, False)
    set_digital(BACK_IN3, False);  set_digital(BACK_IN4, False)

# --- SERVER SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("--- ROBOT SERVER ONLINE ---")
    stop_motors()
    set_servo(SERVO_FRONT, 90)
    set_servo(SERVO_BACK, 90)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Controller Connected!")
    try:
        while True:
            data = await websocket.receive_text()
            cmd = data.strip().upper()
            
            # --- DRIVE LOGIC ---
            if 'W' == cmd: # Forward
                set_digital(FRONT_IN1, True); set_digital(FRONT_IN2, False)
                set_digital(BACK_IN3, True);  set_digital(BACK_IN4, False)
            
            elif 'S' == cmd: # Backward
                set_digital(FRONT_IN1, False); set_digital(FRONT_IN2, True)
                set_digital(BACK_IN3, False);  set_digital(BACK_IN4, True)
            
            elif 'X' == cmd: # Stop
                stop_motors()
            
            # --- SERVO LOGIC ---
            elif cmd.startswith('F'): # Front Servo
                try: set_servo(SERVO_FRONT, int(cmd[1:]))
                except: pass
            
            elif cmd.startswith('B'): # Back Servo
                try: set_servo(SERVO_BACK, int(cmd[1:]))
                except: pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        stop_motors()
        print("Controller Disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)