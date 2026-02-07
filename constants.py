"""
Constants and Configuration Values
Centralized configuration for the voice assistant
"""

# ============================================================================
# GUI CONSTANTS
# ============================================================================

# Window Configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Voice Assistant - وائس اسسٹنٹ"

# Canvas Configuration
CANVAS_WIDTH = 450
CANVAS_HEIGHT = 450

# Animation Parameters
ANIMATION_FPS = 30
ANIMATION_FRAME_DELAY = 33  # milliseconds (1000/30)
BASE_RADIUS = 90
GLOW_RING_COUNT = 6
WAVE_POINTS = 60

# Animation Amplitudes
WAVE_AMP_IDLE = 8
WAVE_AMP_LISTENING = 30
WAVE_AMP_PROCESSING = 20
WAVE_AMP_SPEAKING = 50

# Glow Intensities
GLOW_IDLE = 0.2
GLOW_LISTENING = 0.8
GLOW_PROCESSING = 0.6
GLOW_SPEAKING = 1.0

# Colors
COLOR_BACKGROUND = '#0a0a0a'
COLOR_ACCENT = '#00ff88'
COLOR_SPEAKING = '#ff0088'
COLOR_LISTENING = '#0088ff'
COLOR_PROCESSING = '#ffaa00'
COLOR_IDLE = '#444444'
COLOR_TEXT_SECONDARY = '#888888'
COLOR_TEXT_PRIMARY = '#ffffff'
COLOR_TRANSCRIPT_BG = '#1a1a1a'

# ============================================================================
# TIMEOUT CONSTANTS
# ============================================================================

SUBPROCESS_SHORT_TIMEOUT = 2
SUBPROCESS_MEDIUM_TIMEOUT = 5
SUBPROCESS_LONG_TIMEOUT = 10

PROCESS_TERMINATE_TIMEOUT = 3
PROCESS_KILL_DELAY = 0.5

DEFAULT_LISTEN_TIMEOUT = 5
DEFAULT_PHRASE_TIME_LIMIT = 5
DEFAULT_PAUSE_THRESHOLD = 0.5
DEFAULT_NOISE_ADJUSTMENT = 0.5

INTERNET_CHECK_TIMEOUT = 3
INTERNET_CHECK_CACHE_DURATION = 30
TTS_CACHE_DURATION_DAYS = 7

# ============================================================================
# APPLICATION MAPPINGS
# ============================================================================

APP_PROCESS_MAPPING = {
    'chrome': 'chrome',
    'chromium': 'chromium',
    'firefox': 'firefox',
    'brave': 'brave',
    'terminal': 'gnome-terminal',
    'calculator': 'gnome-calculator',
    'files': 'nautilus',
    'nautilus': 'nautilus',
    'code': 'code',
    'vscode': 'code',
    'gedit': 'gedit',
    'text editor': 'gedit',
    'settings': 'gnome-control-center',
    'music': 'rhythmbox',
    'videos': 'totem',
}

APP_COMMANDS = {
    'chrome': 'google-chrome',
    'chromium': 'chromium-browser',
    'firefox': 'firefox',
    'brave': 'brave-browser',
    'terminal': 'gnome-terminal',
    'calculator': 'gnome-calculator',
    'files': 'nautilus',
    'code': 'code',
    'vscode': 'code',
    'text editor': 'gedit',
    'gedit': 'gedit',
    'settings': 'gnome-control-center',
    'music': 'rhythmbox',
    'videos': 'totem',
    'calendar': 'gnome-calendar',
    'clock': 'gnome-clocks',
}

# ============================================================================
# WEBSITE PATTERNS
# ============================================================================

WEBSITE_PATTERNS = {
    'youtube': ['youtube.com', 'youtube'],
    'gmail': ['gmail.com', 'mail.google.com', 'gmail'],
    'google': ['google.com', 'google.co'],
    'facebook': ['facebook.com', 'fb.com', 'facebook'],
    'twitter': ['twitter.com', 'x.com', 'twitter'],
    'github': ['github.com', 'github'],
    'reddit': ['reddit.com', 'reddit'],
    'linkedin': ['linkedin.com', 'linkedin'],
    'whatsapp': ['web.whatsapp.com', 'whatsapp'],
    'netflix': ['netflix.com', 'netflix'],
    'amazon': ['amazon.com', 'amazon.in', 'amazon'],
    'stackoverflow': ['stackoverflow.com', 'stack overflow'],
}

WEBSITE_URLS = {
    'youtube': 'https://youtube.com',
    'gmail': 'https://gmail.com',
    'google': 'https://google.com',
    'facebook': 'https://facebook.com',
    'twitter': 'https://twitter.com',
    'github': 'https://github.com',
    'reddit': 'https://reddit.com',
    'linkedin': 'https://linkedin.com',
    'whatsapp': 'https://web.whatsapp.com',
    'netflix': 'https://netflix.com',
    'stackoverflow': 'https://stackoverflow.com',
}

# ============================================================================
# COMMAND KEYWORDS
# ============================================================================

EXIT_KEYWORDS_EN = [
    'exit', 'quit', 'stop', 'shutdown assistant',
    'goodbye', 'bye', 'see you', 'stop alexa', 
    'exit alexa', 'goodbye alexa'
]

EXIT_KEYWORDS_UR = ['خدا حافظ', 'رخصت']

SYSTEM_FEATURES = [
    'wifi', 'bluetooth', 'وائی فائی', 'بلوٹوتھ', 
    'volume', 'brightness', 'روشنی', 'آواز'
]

NOISE_WORDS = ['open', 'کھولو', 'کھول', 'the', 'a', 'an']

# ============================================================================
# CHROME PROFILE MAPPINGS
# ============================================================================

CHROME_PROFILE_MAPPING = {
    'me': 'Default',
    'amaan': 'Profile 1',
    'profile 1': 'Profile 1',
    'profile 2': 'Profile 2',
    'work': 'Profile 2',
    'personal': 'Default',
    '1': 'Profile 1',
    '2': 'Profile 2',
}

# ============================================================================
# FILE PATHS
# ============================================================================

DEFAULT_PIPER_MODEL = '~/.local/share/piper/voices/en_US-lessac-medium.onnx'
DEFAULT_TTS_CACHE_DIR = '~/.cache/voice_assistant'
DEFAULT_LOG_FILE = '~/.local/share/voice_assistant/assistant.log'
GUI_STATE_FILE = '/tmp/voice_assistant_state.txt'

MUSIC_EXTENSIONS = ['*.mp3', '*.flac', '*.wav', '*.ogg', '*.m4a']
VIDEO_EXTENSIONS = ['*.mp4', '*.mkv', '*.avi', '*.mov']

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_NO_BROWSER = "No browser is open"
ERROR_NO_TABS = "No browser tabs are open"
ERROR_WMCTRL_MISSING = "wmctrl is not installed. Install it with: sudo apt install wmctrl"
ERROR_NO_MICROPHONE = "Microphone not found or not accessible"
ERROR_NO_INTERNET = "No internet connection"
ERROR_TTS_FAILED = "Text-to-speech is not available"
ERROR_APP_NOT_FOUND = "Application not found or not installed"

# ============================================================================
# VERSION INFO
# ============================================================================

__version__ = "2.1.0-optimized"
__author__ = "Voice Assistant Team"
