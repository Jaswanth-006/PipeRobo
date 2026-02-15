import subprocess
import time
import sys
import os
import signal

# Define the scripts to run
SERVER_SCRIPT = "robot_server.py"
AI_SCRIPT = "ai_pilot.py"

print("🚀 INITIALIZING PIPE-ROBO SYSTEMS...")

# 1. Start the Motor Server (The Body)
print(f"   [1/2] Launching Motor Server ({SERVER_SCRIPT})...")
server_process = subprocess.Popen(
    [sys.executable, SERVER_SCRIPT],
    cwd=os.path.dirname(os.path.abspath(__file__)) # Run in current folder
)

# Wait a moment for the server to fully start
time.sleep(3) 

# 2. Start the AI Vision (The Eyes)
print(f"   [2/2] Launching AI Pilot ({AI_SCRIPT})...")
ai_process = subprocess.Popen(
    [sys.executable, AI_SCRIPT],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

print("\n✅ SYSTEM ONLINE")
print("   - Motor Control: Active (Port 8000)")
print("   - AI Video Feed: Active (Port 5000)")
print("   - Press Ctrl+C to shut down everything.\n")

try:
    # Keep the script running to monitor the processes
    server_process.wait()
    ai_process.wait()

except KeyboardInterrupt:
    print("\n🛑 SHUTTING DOWN...")
    
    # Kill the processes gently
    server_process.terminate()
    ai_process.terminate()
    
    # Wait for them to die
    time.sleep(1)
    
    # Force kill if they are still alive
    if server_process.poll() is None: server_process.kill()
    if ai_process.poll() is None: ai_process.kill()
    
    print("👋 Robot Shutdown Complete.")