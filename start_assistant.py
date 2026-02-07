#!/usr/bin/env python3
"""
Voice Assistant Launcher - Starts GUI in separate process to avoid crashes
"""

import os
import sys
import subprocess
import time

print("🚀 Voice Assistant Launcher")
print("="*60)

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
gui_script = os.path.join(script_dir, 'gui_standalone.py')
state_file = '/tmp/voice_assistant_state.txt'

# Check if GUI script exists
if not os.path.exists(gui_script):
    print(f"❌ Error: GUI script not found at {gui_script}")
    sys.exit(1)

print("1️⃣  Starting GUI in separate process...")

# Start GUI process
try:
    gui_process = subprocess.Popen(
        [sys.executable, gui_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(f"✅ GUI process started (PID: {gui_process.pid})")
except Exception as e:
    print(f"❌ Failed to start GUI: {e}")
    sys.exit(1)

# Wait for GUI to initialize
print("2️⃣  Waiting for GUI to initialize...")
time.sleep(2)

# Check if GUI is still running
if gui_process.poll() is not None:
    print("❌ GUI process exited unexpectedly")
    print("STDOUT:", gui_process.stdout.read().decode())
    print("STDERR:", gui_process.stderr.read().decode())
    sys.exit(1)

print("✅ GUI is running!")
print("3️⃣  Starting voice assistant...")

# Now start the voice assistant in THIS process
from voice_assistant_advanced import VoiceAssistant

class GUIBridge:
    """Bridge to communicate with GUI via file"""
    
    def __init__(self, state_file):
        self.state_file = state_file
        self.root = None  # Dummy for compatibility
    
    def winfo_exists(self):
        return os.path.exists(self.state_file)
    
    # Define all the methods that assistant will call
    def set_idle(self):
        self.write_state('STATE|idle')
        self.write_state('STATUS|💤 Waiting for wake word...|#888888')
    
    def set_listening(self):
        self.write_state('STATE|listening')
        self.write_state('STATUS|🎤 Listening...|#0088ff')
    
    def set_speaking(self, text=""):
        short = text[:30] + "..." if len(text) > 30 else text
        self.write_state('STATE|speaking')
        self.write_state(f'STATUS|🗣️ {short}|#ff0088')
    
    def set_processing(self):
        self.write_state('STATE|processing')
        self.write_state('STATUS|⚙️ Processing...|#ffaa00')
    
    def add_user_message(self, text, lang='en'):
        self.write_state(f'MSG|user|{text}')
    
    def add_assistant_message(self, text, lang='en'):
        self.write_state(f'MSG|assistant|{text}')
    
    def add_system_message(self, text):
        self.write_state(f'MSG|system|{text}')
    
    def queue_update(self, func, *args):
        """Queue update by calling the function directly"""
        try:
            # Just call the function since we're not threading
            func(*args)
        except Exception as e:
            pass
    
    def write_state(self, data):
        """Write to state file"""
        try:
            with open(self.state_file, 'w') as f:
                f.write(data)
            time.sleep(0.01)  # Small delay for file system
        except:
            pass

# Create bridge
gui = GUIBridge(state_file)

# Write initial message
gui.queue_update(gui.add_system_message, "🚀 Voice Assistant Starting...")

try:
    # Initialize assistant
    config_path = 'config.ini'
    if not os.path.exists(config_path):
        config_path = os.path.join(script_dir, 'config.ini')
    
    assistant = VoiceAssistant(config_path, gui=gui)
    
    gui.queue_update(gui.add_system_message, "✅ Assistant Loaded!")
    gui.queue_update(gui.add_system_message, "🎤 Say 'alexa' to activate")
    
    print("✅ Assistant initialized")
    print("🎤 Voice recognition active")
    print("\n" + "="*60)
    print("GUI is running in separate window")
    print("This terminal shows voice assistant status")
    print("Close the GUI window or press Ctrl+C to exit")
    print("="*60 + "\n")
    
    # Run assistant
    assistant.run()
    
except KeyboardInterrupt:
    print("\n👋 Interrupted by user")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Signal GUI to close
    try:
        with open(state_file, 'w') as f:
            f.write('EXIT|assistant')
    except:
        pass
    
    # Wait a bit then terminate GUI
    time.sleep(0.5)
    if gui_process.poll() is None:
        gui_process.terminate()
        time.sleep(0.5)
        if gui_process.poll() is None:
            gui_process.kill()
    
    print("✅ Exited cleanly")
