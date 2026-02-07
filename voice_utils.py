"""
Utility functions for the bilingual voice assistant
"""

import socket
import subprocess
import os
import logging
from datetime import datetime, timedelta
import configparser

logger = logging.getLogger(__name__)

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_file):
    """Setup logging configuration"""
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config(config_path='config.ini'):
    """Load configuration from file with defaults"""
    config = configparser.ConfigParser()
    
    # Default configuration
    defaults = {
        'General': {
            'wake_word': 'alexa',
            'wake_word_ur': 'الیکسا',
            'default_language': 'auto',
            'enable_history': 'true',
            'max_history_items': '10'
        },
        'Speech Recognition': {
            'listen_timeout': '5',
            'phrase_time_limit': '5',
            'pause_threshold': '0.5',
            'noise_adjustment': '0.5',
            'energy_threshold': 'auto'
        },
        'Text-to-Speech': {
            'preferred_tts': 'auto',
            'piper_rate': '165',
            'enable_tts_cache': 'true',
            'cache_duration_days': '7'
        },
        'Features': {
            'enable_wake_word': 'true',
            'enable_web_search': 'true',
            'enable_app_control': 'true',
            'enable_system_control': 'true',
            'enable_file_management': 'true',
            'enable_multimedia': 'true'
        },
        'System': {
            'confirm_shutdown': 'true',
            'confirm_delete': 'true',
            'browser': 'firefox',
            'file_manager': 'nautilus',
            'text_editor': 'gedit',
            'terminal': 'gnome-terminal',
            'music_player': 'rhythmbox',
            'video_player': 'totem'
        },
        'Paths': {
            'piper_model': '~/.local/share/piper/voices/en_US-lessac-medium.onnx',
            'cache_dir': '~/.cache/voice_assistant',
            'log_file': '~/.local/share/voice_assistant/assistant.log'
        }
    }
    
    if os.path.exists(config_path):
        config.read(config_path)
        # Fill in any missing sections/options with defaults
        for section, options in defaults.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in options.items():
                if not config.has_option(section, key):
                    config.set(section, key, value)
    else:
        config.read_dict(defaults)
        logger.warning(f"Config file not found at {config_path}, using defaults")
    
    return config

# ============================================================================
# INTERNET CONNECTIVITY
# ============================================================================

class InternetChecker:
    """Check internet connectivity with caching"""
    
    def __init__(self, cache_duration=30):
        self.cache_duration = cache_duration
        self.last_check = None
        self.last_result = False
    
    def is_connected(self):
        """Check internet connectivity with caching"""
        now = datetime.now()
        
        if self.last_check and (now - self.last_check).seconds < self.cache_duration:
            return self.last_result
        
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.last_result = True
        except OSError:
            self.last_result = False
        
        self.last_check = now
        return self.last_result

# ============================================================================
# CONVERSATION HISTORY
# ============================================================================

class ConversationHistory:
    """Manage conversation history"""
    
    def __init__(self, max_items=10):
        self.max_items = max_items
        self.history = []
    
    def add(self, user_input, assistant_response, language='en'):
        """Add a conversation entry"""
        entry = {
            'timestamp': datetime.now(),
            'user': user_input,
            'assistant': assistant_response,
            'language': language
        }
        
        self.history.append(entry)
        
        if len(self.history) > self.max_items:
            self.history.pop(0)
    
    def get_recent(self, n=5):
        """Get n most recent entries"""
        return self.history[-n:]
    
    def clear(self):
        """Clear history"""
        self.history = []

# ============================================================================
# TTS CACHE
# ============================================================================

class TTSCache:
    """Manage TTS audio caching"""
    
    def __init__(self, cache_dir, duration_days=7):
        self.cache_dir = os.path.expanduser(cache_dir)
        self.duration_days = duration_days
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cache_path(self, text, lang='en'):
        """Get cache file path for given text"""
        import hashlib
        text_hash = hashlib.md5(f"{text}_{lang}".encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.mp3")
    
    def exists(self, text, lang='en'):
        """Check if cached audio exists and is valid"""
        cache_path = self.get_cache_path(text, lang)
        
        if not os.path.exists(cache_path):
            return False
        
        # Check if cache is expired
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - file_time > timedelta(days=self.duration_days):
            os.remove(cache_path)
            return False
        
        return True
    
    def get(self, text, lang='en'):
        """Get cached audio file path"""
        if self.exists(text, lang):
            return self.get_cache_path(text, lang)
        return None
    
    def save(self, text, audio_file, lang='en'):
        """Save audio to cache"""
        cache_path = self.get_cache_path(text, lang)
        import shutil
        shutil.copy2(audio_file, cache_path)
    
    def clear_old(self):
        """Clear expired cache files"""
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if datetime.now() - file_time > timedelta(days=self.duration_days):
                os.remove(filepath)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    dangerous_chars = ['/', '\\', '..', '~', '$', '`', '|', ';', '&', '>', '<', '*', '?', '"', "'"]
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized[:255].strip()

def command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run(['which', command], 
                      capture_output=True, 
                      check=True, 
                      timeout=2)
        return True
    except:
        return False
