#!/usr/bin/env python3
"""
Quick test to see where it's hanging
"""

print("1. Testing imports...")
try:
    from voice_utils import load_config
    print("   ✅ voice_utils")
except Exception as e:
    print(f"   ❌ voice_utils: {e}")
    exit(1)

try:
    from speech_recognition_module import SpeechRecognizer
    print("   ✅ speech_recognition_module")
except Exception as e:
    print(f"   ❌ speech_recognition_module: {e}")
    print("   → Run: pip install SpeechRecognition pyaudio --break-system-packages")
    exit(1)

try:
    from tts_engine import TTSEngine
    print("   ✅ tts_engine")
except Exception as e:
    print(f"   ❌ tts_engine: {e}")
    exit(1)

print("\n2. Testing config load...")
config = load_config('config.ini')
print("   ✅ Config loaded")

print("\n3. Testing SpeechRecognizer init...")
try:
    recognizer = SpeechRecognizer(config)
    print("   ✅ SpeechRecognizer initialized")
except Exception as e:
    print(f"   ❌ SpeechRecognizer failed: {e}")
    print("   → This might be a microphone issue")

print("\n✅ All basic tests passed!")
print("\nIf it hung here, the issue is with microphone initialization.")
print("Try running with --no-gui flag:")
print("  python3 voice_assistant_advanced.py --no-gui")
