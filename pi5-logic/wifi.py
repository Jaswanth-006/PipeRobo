import socket
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

# --- HARDWARE SETUP ---
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 60

LEFT_IN1, LEFT_IN2 = 0, 1
RIGHT_IN3, RIGHT_IN4 = 2, 3
SERVO_FRONT, SERVO_BACK = 15, 14
SERVOMIN, SERVOMAX = 150, 720 

# --- APP CONFIGURATION ---
SERVER_IP = '10.148.173.95'  # IP from App
SERVER_PORT = 50123          # Port from App

def set_digital(channel, state):
    if state: pca.channels[channel].duty_cycle = 0xFFFF
    else: pca.channels[channel].duty_cycle = 0

def set_servo(channel, angle):
    angle = max(0, min(180, angle))
    pulse = int(SERVOMIN + (angle / 180.0) * (SERVOMAX - SERVOMIN))
    duty = int((pulse / 4096) * 65535)
    pca.channels[channel].duty_cycle = duty

def stop_motors():
    set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, False)
    set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, False)

# --- MAIN LOOP ---
print(f"--- CONNECTING TO RAW TCP SERVER ---")
print(f"Target: {SERVER_IP}:{SERVER_PORT}")

stop_motors()
set_servo(SERVO_FRONT, 90)
set_servo(SERVO_BACK, 90)

while True:
    try:
        # Create Socket (NO TIMEOUT set this time)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        print("Attempting to connect...")
        s.connect((SERVER_IP, SERVER_PORT))
        print("\n>>> SUCCESS! CONNECTED TO APP <<<")
        print("Go ahead! Press buttons on your phone now.\n")
        
        while True:
            # Buffer size 1024 bytes
            data = s.recv(1024)
            
            # If data is empty, server/app disconnected
            if not data: 
                print("App closed connection.")
                break
            
            # Decode and Print
            raw_data = data.decode('utf-8', errors='ignore')
            cmd = raw_data.strip().upper()
            
            # Print exact data (Useful for debugging)
            print(f"Received Command: [{cmd}]") 
            
            # --- MOVEMENT MAPPING ---
            # NOTE: We check 'if X in cmd' because sometimes 
            # the app sends "Forward\n" or "Fwd" instead of just "F"
            
            if 'W' in cmd:         # Forward
                set_digital(LEFT_IN1, True); set_digital(LEFT_IN2, False)
                set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, True)
                
            elif 'S' in cmd:       # Backward
                set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, True)
                set_digital(RIGHT_IN3, True); set_digital(RIGHT_IN4, False)
                
            elif 'L' in cmd:       # Left
                set_servo(SERVO_FRONT, 45); set_servo(SERVO_BACK, 135)
                
            elif 'R' in cmd:       # Right
                set_servo(SERVO_FRONT, 135); set_servo(SERVO_BACK, 45)
                
            elif 'X' in cmd or 'X' in cmd: # Stop
                stop_motors()
                set_servo(SERVO_FRONT, 90); set_servo(SERVO_BACK, 90)

        s.close()
        stop_motors()
        print("Reconnecting in 3 seconds...")
        time.sleep(3)
        
    except ConnectionRefusedError:
        print("Connection Refused. Is the App Open and Listening?")
        time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
        stop_motors()
        time.sleep(2)
