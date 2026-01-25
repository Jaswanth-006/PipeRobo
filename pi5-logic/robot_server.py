import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

# --- HARDWARE SETUP (From your working script) ---
try:
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c)
    pca.frequency = 60
except:
    print("Hardware not found! Running in Simulation Mode.")
    pca = None

# Your Pins
LEFT_IN1, LEFT_IN2 = 0, 1
RIGHT_IN3, RIGHT_IN4 = 2, 3
SERVO_FRONT, SERVO_BACK = 15, 14

# Your Calibration
SERVOMIN, SERVOMAX = 150, 720 

# --- HELPER FUNCTIONS ---
def set_digital(channel, state):
    if pca is None: return
    if state: pca.channels[channel].duty_cycle = 0xFFFF
    else: pca.channels[channel].duty_cycle = 0

def set_servo(channel, angle):
    if pca is None: return
    angle = max(0, min(180, angle))
    # Your exact formula
    pulse = int(SERVOMIN + (angle / 180.0) * (SERVOMAX - SERVOMIN))
    duty = int((pulse / 4096) * 65535)
    pca.channels[channel].duty_cycle = duty

def stop_motors():
    set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, False)
    set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, False)

# --- SERVER SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
    print("React App Connected!")
    try:
        while True:
            data = await websocket.receive_text()
            cmd = data.strip().upper()
            print(f"CMD: {cmd}")

            # --- MOTOR LOGIC (Matched to your previous script) ---
            if 'W' == cmd:
                # Forward (Left: T/F, Right: F/T based on your previous valid code)
                set_digital(LEFT_IN1, True); set_digital(LEFT_IN2, False)
                set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, True)
            
            elif 'S' == cmd:
                # Backward
                set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, True)
                set_digital(RIGHT_IN3, True); set_digital(RIGHT_IN4, False)
            
            elif 'X' == cmd:
                stop_motors()
            
            # --- SERVO LOGIC ---
            elif cmd.startswith('F'): # Front Servo
                try:
                    angle = int(cmd[1:]) # Reads "F45" as 45
                    set_servo(SERVO_FRONT, angle)
                except: pass
            
            elif cmd.startswith('B'): # Back Servo
                try:
                    angle = int(cmd[1:]) # Reads "B135" as 135
                    set_servo(SERVO_BACK, angle)
                except: pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        stop_motors()
        print("Client Disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
