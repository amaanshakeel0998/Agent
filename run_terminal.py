#!/usr/bin/env python3
"""
Simple Voice Assistant Runner - No GUI, Terminal Only
Use this if GUI version hangs
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🎤 Starting Voice Assistant (Terminal Mode)")
print("=" * 60)

# Check config
config_path = 'config.ini'
if not os.path.exists(config_path):
    print("❌ Error: config.ini not found!")
    print("   Make sure you're in the correct directory")
    exit(1)

print("✅ Config found")
print("🚀 Initializing assistant...\n")

# Import and run
try:
    from voice_assistant_advanced import VoiceAssistant
    
    # Create assistant without GUI
    assistant = VoiceAssistant(config_path, gui=None)
    
    print("\n✅ Assistant ready!")
    print("🎤 Listening for commands...")
    print("=" * 60)
    print()
    
    # Run
    assistant.run()
    
except KeyboardInterrupt:
    print("\n\n👋 Exited by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Try installing dependencies:")
    print("   chmod +x setup.sh && ./setup.sh")
