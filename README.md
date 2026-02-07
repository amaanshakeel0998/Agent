# Advanced Bilingual Voice Assistant (Optimized)
## پیشرفتہ دو لسانی وائس اسسٹنٹ

**Version:** 2.1.0-optimized  
**Optimized for:** All features + Future enhancements
**Developer Name:** Muhammad Amaan

## Extra Info
The current owner name saved in this project is "Amaan", when you ask the name of the owner it said "Amaan", So for this you can edit it first.

## 📁 Final File Structure

```
voice_assistant/
├── voice_assistant_advanced.py    # Main application (1202 lines)
├── start_assistant.py             # Launcher (stable GUI mode)
├── gui_standalone.py              # GUI interface
├── config.ini                     # User configuration
│
├── Core Modules:
├── speech_recognition_module.py   # Speech recognition + wake word
├── tts_engine.py                  # Text-to-speech (gTTS + Piper)
├── voice_utils.py                 # Utilities (optimized)
├── constants.py                   # Constants (optimized)
├── error_handling.py              # Error handling (optimized)
│
├── Feature Modules:
├── context_manager.py             # App tracking & memory
├── browser_tab_manager.py         # Browser tab control
├── system_actions.py              # System controls (brightness, WiFi, etc.)
├── multimedia_actions.py          # Media & volume controls
│
└── Setup:
    └── setup.sh                   # Installation script
```

**Total:** 14 files (down from 20+)

---

## ✨ All Features (Fully Working)

### Core Features
- 🎤 **Bilingual Speech Recognition** - English + Urdu
- 🗣️ **Smart TTS** - Auto-switches between gTTS (online) & Piper (offline)
- 🎯 **Wake Word Detection** - "alexa" / "الیکسا"
- 🧠 **Context Awareness** - Remembers apps, understands "it", "that"
- 📝 **Conversation History** - Last 10 interactions
- 💾 **TTS Caching** - Faster repeated phrases
- 🎨 **Beautiful GUI** - Animated visualizer (ready for enhancement)
- 🖥️ **Terminal Mode** - Debugging support

### System Control
- 🔆 Brightness (increase/decrease/set percentage)
- 📡 WiFi (on/off/status)
- 🔵 Bluetooth (on/off)
- 🔋 Battery info
- 💾 Disk & Memory info
- 🔒 Lock screen
- ⚡ Power (shutdown/restart/sleep/logout)

### Browser & Tabs
- 🌐 Open websites
- 🔍 Web search
- 📑 Switch to open tabs (YouTube, Gmail, etc.)
- ❌ Close tabs
- 📊 List open tabs

### Multimedia
- 🎵 Music control (play/pause/next/previous)
- 🎚️ Volume control (set percentage)
- 📸 Screenshots
- 🎧 Get current track

### Applications
- 🚀 Open any app (Chrome, Firefox, Terminal, Calculator, etc.)
- ❌ Close apps (context-aware: "close it")
- 📁 File manager
- ⚙️ Settings
- 🎨 Custom app support

---

## 📦 Installation

### Quick Setup:
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Installation:
```bash
# Python packages
pip install gtts SpeechRecognition pyaudio langdetect psutil --break-system-packages

# System dependencies
sudo apt install -y mpg123 espeak portaudio19-dev python3-pyaudio \
    alsa-utils gnome-screenshot playerctl brightnessctl xdotool \
    network-manager bluez wmctrl

# Piper TTS (offline English)
cd /tmp
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper/piper /usr/local/bin/

# Voice model
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

---

## 🚀 Usage

### With GUI (Recommended):
```bash
python3 start_assistant.py
```
or
```bash
python3 voice_assistant_advanced.py
```

### Terminal Only (for debugging):
```bash
python3 voice_assistant_advanced.py --no-gui
```

---

## 🎯 Example Commands

### English:
```
"Alexa, open YouTube"
"Alexa, what time is it?"
"Alexa, increase brightness"
"Alexa, turn on WiFi"
"Alexa, play music"
"Alexa, close it"  (closes last opened app)
"Alexa, what tabs are open?"
"Alexa, switch to Gmail"
```

### Urdu:
```
"الیکسا، یوٹیوب کھولو"
"الیکسا، وقت کیا ہوا ہے؟"
"الیکسا، روشنی بڑھاؤ"
"الیکسا، وائی فائی چالو کرو"
"الیکسا، موسیقی چلاؤ"
```

### Context-Aware:
```
You: "Alexa, open Chrome"
Alexa: "Opening chrome"

You: "Alexa, close it"
Alexa: "Closed chrome"
```

---

## ⚙️ Configuration

Edit `config.ini`:

### Wake Word:
```ini
[General]
wake_word = alexa           # Change to your preference
wake_word_ur = الیکسا        # Urdu wake word
```

### TTS Preference:
```ini
[Text-to-Speech]
preferred_tts = auto        # auto/gtts/piper
enable_tts_cache = true     # Cache for speed
```

### Features:
```ini
[Features]
enable_wake_word = true         # false = always listening
enable_web_search = true
enable_system_control = true
enable_multimedia = true
```

### Default Apps:
```ini
[System]
browser = firefox
terminal = gnome-terminal
text_editor = gedit
music_player = rhythmbox
```

---

## 🎨 GUI Enhancement (For Future)

The current GUI (`gui_standalone.py`) has:
- ✅ Animated waveform visualizer
- ✅ Real-time status updates
- ✅ Conversation transcript
- ✅ Smooth animations

**Ideas for enhancement:**
1. Add themes (dark/light/custom colors)
2. Settings panel in GUI
3. Voice feedback visualization (bars/spectrum)
4. Mini mode (compact version)
5. System tray integration
6. Keyboard shortcuts
7. Command history viewer
8. Visual feedback for each command type

---

## 🔧 Code Organization (For Future Development)

### Adding New Commands:

**In `voice_assistant_advanced.py`:**
```python
# Around line 600-900, in process_command() method
elif 'your command' in command_lower:
    # Your logic here
    self.speak("Response", lang)
```

### Adding New Features:

1. **New module:** Create `your_feature.py`
2. **Import:** Add to `voice_assistant_advanced.py`
3. **Initialize:** In `__init__` method
4. **Use:** In `process_command` method

### Adding New Apps:

**In `constants.py`:**
```python
APP_COMMANDS = {
    'your_app': 'command-to-launch',
    # ...existing apps
}
```

---

## 🐛 Troubleshooting

### Microphone Issues:
```bash
# Test microphone
arecord -l
arecord -d 5 test.wav && aplay test.wav
```

### GUI Not Showing:
```bash
# Use terminal mode for debugging
python3 voice_assistant_advanced.py --no-gui
```

### TTS Not Working:
```bash
# Check gTTS (needs internet)
echo "test" | gtts-cli - | mpg123 -

# Check Piper (offline)
echo "test" | piper --model ~/.local/share/piper/voices/en_US-lessac-medium.onnx --output_file test.wav
aplay test.wav
```

### Import Errors:
```bash
# Reinstall dependencies
pip install --force-reinstall gtts SpeechRecognition pyaudio langdetect psutil --break-system-packages
```

---

## 📊 Performance Metrics

**Before optimization:**
- 20+ files
- ~5000 lines total
- Many unused constants
- Duplicate code

**After optimization:**
- 14 files
- ~3500 lines total
- All code is used
- No duplicates

**Reduction:** ~35% code reduction while keeping ALL features!

---

## 🎓 Technical Details

### Architecture:
```
User Voice
    ↓
Speech Recognition Module
    ↓
Voice Assistant (Main Logic)
    ├→ Context Manager (Remember apps)
    ├→ Browser Tab Manager
    ├→ System Actions
    ├→ Multimedia Actions
    ↓
TTS Engine (gTTS/Piper)
    ↓
Audio Output
```

### Threading Model:
- **Main thread:** GUI + User input
- **Worker thread:** TTS queue processing
- **Background thread:** Voice recognition loop

### Caching Strategy:
- **TTS Cache:** 7 days (configurable)
- **Internet Check:** 30 seconds cache
- **Tab Detection:** Real-time (no cache)

---

## 📝 Logs

```bash
# View logs
tail -f ~/.local/share/voice_assistant/assistant.log

# Clear old logs
rm ~/.local/share/voice_assistant/assistant.log
```

---

## 🚀 Future Enhancement Roadmap

### Short-term (Easy):
- [ ] Add more Chrome profiles
- [ ] Custom wake words
- [ ] More Urdu commands
- [ ] GUI themes
- [ ] Keyboard shortcuts

### Medium-term:
- [ ] Email integration (Gmail)
- [ ] Calendar integration
- [ ] Reminders/Timers
- [ ] Smart home control
- [ ] File operations (search, open, move)

### Long-term (Advanced):
- [ ] Custom wake word training (Porcupine)
- [ ] Local LLM integration
- [ ] Multi-room support
- [ ] Mobile app companion
- [ ] Plugin system

---

## 📄 License

Personal project - Free to use and modify!

---

## 🙏 Credits

- **gTTS** - Google Text-to-Speech
- **Piper** - Offline TTS by Rhasspy
- **SpeechRecognition** - Python library
- **Anthropic Claude** - Development assistance

---

**Enjoy your optimized voice assistant! 🎉**  
**اپنے بہتر شدہ وائس اسسٹنٹ سے لطف اٹھائیں! 🎉**
