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
            
            # 1. DRIVE COMMANDS (Your Custom Logic)
            if 'W' in cmd:         # Forward
                set_digital(LEFT_IN1, True); set_digital(LEFT_IN2, False)
                set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, True)
                
            elif 'S' in cmd:       # Backward
                set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, True)
                set_digital(RIGHT_IN3, True); set_digital(RIGHT_IN4, False)
                
            elif 'X' in cmd:       # Stop
                stop_motors()
                # Optional: Re-center servos on Stop? 
                # Uncomment next line if you want that:
                # set_servo(SERVO_FRONT, 90); set_servo(SERVO_BACK, 90)

            # 2. SERVO COMMANDS (F<angle> and B<angle>)
            elif cmd.startswith('F'):
                try:
                    # Remove 'F' and grab the number (e.g., F135 -> 135)
                    angle_str = cmd.replace('F', '')
                    if angle_str.isdigit():
                        angle = int(angle_str)
                        set_servo(SERVO_FRONT, angle)
                        print(f"Front Servo: {angle}")
                except ValueError:
                    pass

            elif cmd.startswith('B'):
                try:
                    # Remove 'B' and grab the number
                    angle_str = cmd.replace('B', '')
                    if angle_str.isdigit():
                        angle = int(angle_str)
                        set_servo(SERVO_BACK, angle)
                        print(f"Back Servo: {angle}")
                except ValueError:
                    pass

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
