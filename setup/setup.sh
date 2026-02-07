#!/bin/bash

echo "=============================================="
echo "Advanced Bilingual Voice Assistant Setup"
echo "پیشرفتہ دو لسانی وائس اسسٹنٹ سیٹ اپ"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

echo "📦 Step 1: Installing Python packages..."
pip install gtts SpeechRecognition pyaudio langdetect --break-system-packages

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python packages installed${NC}"
else
    echo -e "${YELLOW}⚠️  Some Python packages may have failed. Trying with --user flag...${NC}"
    pip install --user gtts SpeechRecognition pyaudio langdetect
fi

echo ""
echo "📦 Step 2: Installing system packages..."
sudo apt update
sudo apt install -y \
    mpg123 \
    espeak \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    gnome-screenshot \
    playerctl \
    brightnessctl \
    xdotool \
    network-manager \
    bluez \
    wmctrl

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ System packages installed${NC}"
else
    echo -e "${RED}❌ Some system packages failed to install${NC}"
    echo "Please install them manually"
fi

echo ""
echo "📦 Step 3: Installing Piper TTS (for offline English)..."

cd /tmp
wget -q --show-progress https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz

if [ $? -eq 0 ]; then
    tar -xzf piper_amd64.tar.gz
    sudo mv piper/piper /usr/local/bin/
    rm -rf piper piper_amd64.tar.gz
    echo -e "${GREEN}✅ Piper TTS installed${NC}"
else
    echo -e "${RED}❌ Piper download failed${NC}"
fi

echo ""
echo "📦 Step 4: Downloading English voice model..."

mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices

wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Voice model downloaded${NC}"
else
    echo -e "${RED}❌ Voice model download failed${NC}"
fi

echo ""
echo "📦 Step 5: Creating directories..."

mkdir -p ~/.cache/voice_assistant
mkdir -p ~/.local/share/voice_assistant
mkdir -p ~/Pictures

echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Features installed:"
echo "  ✅ English + Urdu speech recognition"
echo "  ✅ Automatic language detection"
echo "  ✅ gTTS for smooth voices (online)"
echo "  ✅ Piper for offline English"
echo "  ✅ Wake word detection"
echo "  ✅ System controls (brightness, WiFi, etc.)"
echo "  ✅ Multimedia controls"
echo "  ✅ TTS caching"
echo "  ✅ Conversation history"
echo ""
echo "Run the assistant with:"
echo "  python3 voice_assistant_advanced.py"
echo ""
echo "Configuration file: config.ini"
echo "Log file: ~/.local/share/voice_assistant/assistant.log"
echo ""
echo "دونوں زبانوں میں کمانڈز کام کرتی ہیں!"
echo ""
