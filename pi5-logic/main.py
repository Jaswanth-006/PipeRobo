import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# Initialize I2C and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 60

# --- CONFIGURATION ---
LEFT_IN1, LEFT_IN2 = 0, 1
RIGHT_IN3, RIGHT_IN4 = 2, 3
SERVO_FRONT_CH, SERVO_BACK_CH = 15, 14

# Calibration (Matching your ESP32 'Stretched' pulses)
# Pulse range 150-720 on 12-bit (4096) scale
SERVOMIN = 150
SERVOMAX = 720

def set_digital(channel, state):
    """Simulates HIGH/LOW for motor driver pins"""
    if state:
        pca.channels[channel].duty_cycle = 0xFFFF  # 100% duty cycle
    else:
        pca.channels[channel].duty_cycle = 0x0000  # 0% duty cycle

def set_servo(channel, angle):
    """Maps 0-180 degrees to your specific pulse range"""
    # Constrain angle
    angle = max(0, min(180, angle))
    # Map angle to pulse (Linear interpolation)
    pulse = int(SERVOMIN + (angle / 180.0) * (SERVOMAX - SERVOMIN))
    # Convert pulse (out of 4096) to 16-bit duty cycle
    duty = int((pulse / 4096) * 65535)
    pca.channels[channel].duty_cycle = duty

def stop_motors():
    set_digital(LEFT_IN1, False)
    set_digital(LEFT_IN2, False)
    set_digital(RIGHT_IN3, False)
    set_digital(RIGHT_IN4, False)

# --- MAIN LOOP ---
try:
    print("System Ready. Use W/S/X for motors, F/B for servos.")
    # Set initial positions
    set_servo(SERVO_FRONT_CH, 90)
    set_servo(SERVO_BACK_CH, 90)

    while True:
        command = input("Enter command: ").upper()
        
        if command == 'W':
            set_digital(LEFT_IN1, True); set_digital(LEFT_IN2, False)
            set_digital(RIGHT_IN3, False); set_digital(RIGHT_IN4, True)
            print("Motor: FWD")
        elif command == 'S':
            set_digital(LEFT_IN1, False); set_digital(LEFT_IN2, True)
            set_digital(RIGHT_IN3, True); set_digital(RIGHT_IN4, False)
            print("Motor: BCK")
        elif command == 'X':
            stop_motors()
            print("Motor: STOP")
        elif command.startswith('F'):
            angle = int(command[1:])
            set_servo(SERVO_FRONT_CH, angle)
            print(f"Front Servo: {angle}")
        elif command.startswith('B'):
            angle = int(command[1:])
            set_servo(SERVO_BACK_CH, angle)
            print(f"Back Servo: {angle}")

except KeyboardInterrupt:
    stop_motors()
    pca.deinit()
