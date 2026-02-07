"""
Text-to-Speech Engine with threading and caching support
"""

import subprocess
import tempfile
import os
import threading
from queue import Queue
import logging

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self, config, internet_checker, tts_cache=None):
        self.config = config
        self.internet_checker = internet_checker
        self.tts_cache = tts_cache
        self.current_mode = None
        self.tts_queue = Queue()
        self.is_speaking = False
        self.stop_speaking = threading.Event()
        
        # Start TTS worker thread
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.worker_thread.start()
    
    def _check_piper(self):
        """Check if Piper TTS is installed"""
        try:
            result = subprocess.run(['piper', '--version'], 
                                  capture_output=True, 
                                  timeout=2)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _speak_with_gtts(self, text, lang='en'):
        """Speak using Google TTS (online)"""
        try:
            # Check cache first
            if self.tts_cache:
                cached_file = self.tts_cache.get(text, lang)
                if cached_file:
                    logger.debug(f"Using cached TTS for: {text[:30]}...")
                    # Try multiple audio backends
                    try:
                        subprocess.run(['mpg123', '-q', cached_file], check=True)
                    except:
                        try:
                            subprocess.run(['ffplay', '-nodisp', '-autoexit', cached_file], check=True, stderr=subprocess.DEVNULL)
                        except:
                            subprocess.run(['paplay', cached_file], check=True)
                    return True
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_file)
            
            # Save to cache
            if self.tts_cache:
                self.tts_cache.save(text, temp_file, lang)
            
            # Play the audio
            subprocess.run(['mpg123', '-q', temp_file], check=True)
            
            # Clean up (cache keeps its copy)
            os.unlink(temp_file)
            return True
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return False
    
    def _speak_with_piper(self, text, lang='en'):
        """Speak using Piper TTS (offline) - English only"""
        if lang == 'ur':
            logger.warning("Piper doesn't support Urdu")
            return False
        
        try:
            voice_model = os.path.expanduser(
                self.config.get('Paths', 'piper_model', 
                               fallback='~/.local/share/piper/voices/en_US-lessac-medium.onnx')
            )
            
            if not os.path.exists(voice_model):
                logger.error(f"Piper model not found: {voice_model}")
                return False
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                temp_file = fp.name
            
            # Generate speech
            process = subprocess.Popen(
                ['piper', '--model', voice_model, '--output_file', temp_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate(input=text.encode())
            
            # Play the audio
            subprocess.run(['aplay', '-q', temp_file], check=True)
            
            # Clean up
            os.unlink(temp_file)
            return True
        except Exception as e:
            logger.error(f"Piper error: {e}")
            return False
    
    def _tts_worker(self):
        """Worker thread for processing TTS queue"""
        while True:
            item = self.tts_queue.get()
            
            if item is None:  # Shutdown signal
                break
            
            text, lang = item
            self.is_speaking = True
            self.stop_speaking.clear()
            
            # Try speaking
            has_internet = self.internet_checker.is_connected()
            
            if has_internet and GTTS_AVAILABLE:
                if self.current_mode != "gTTS":
                    logger.info(f"Using Google TTS - {lang}")
                    self.current_mode = "gTTS"
                self._speak_with_gtts(text, lang)
            elif lang == 'en' and self._check_piper():
                if self.current_mode != "Piper":
                    logger.info("Using Piper TTS - English")
                    self.current_mode = "Piper"
                self._speak_with_piper(text, lang)
            else:
                logger.warning("No suitable TTS available")
            
            self.is_speaking = False
            self.tts_queue.task_done()
    
    def speak(self, text, lang='en', block=False):
        """Add text to speech queue"""
        logger.info(f"Speaking ({lang}): {text}")
        self.tts_queue.put((text, lang))
        
        if block:
            self.tts_queue.join()
    
    def speak_async(self, text, lang='en'):
        """Speak asynchronously (non-blocking)"""
        self.speak(text, lang, block=False)
    
    def wait_until_done(self):
        """Wait until all queued speech is done"""
        self.tts_queue.join()
    
    def stop(self):
        """Stop current speech"""
        self.stop_speaking.set()
        # Clear queue
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
                self.tts_queue.task_done()
            except:
                pass
    
    def shutdown(self):
        """Shutdown TTS engine"""
        self.tts_queue.put(None)
        self.worker_thread.join()
