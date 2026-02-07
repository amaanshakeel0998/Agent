"""
Speech Recognition module with wake word detection
"""

import speech_recognition as sr
import re
import logging

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()
        
        # Get settings from config
        self.listen_timeout = config.getint('Speech Recognition', 'listen_timeout', fallback=5)
        self.phrase_time_limit = config.getint('Speech Recognition', 'phrase_time_limit', fallback=5)
        self.pause_threshold = config.getfloat('Speech Recognition', 'pause_threshold', fallback=0.5)
        self.noise_adjustment = config.getfloat('Speech Recognition', 'noise_adjustment', fallback=0.5)
        
        self.recognizer.pause_threshold = self.pause_threshold
        
        # Wake words
        self.wake_word_en = config.get('General', 'wake_word', fallback='alexa').lower()
        self.wake_word_ur = config.get('General', 'wake_word_ur', fallback='الیکسا')
        self.wake_word_enabled = config.getboolean('Features', 'enable_wake_word', fallback=True)
    
    def detect_language(self, text):
        """Detect if text is in English or Urdu"""
        if not LANGDETECT_AVAILABLE:
            # Fallback: check for Urdu Unicode range
            urdu_pattern = re.compile(r'[\u0600-\u06FF]+')
            if urdu_pattern.search(text):
                return 'ur'
            return 'en'
        
        try:
            lang = detect(text)
            if lang in ['ur', 'pa', 'hi']:
                return 'ur'
            return 'en'
        except:
            return 'en'
    
    def check_wake_word(self, text):
        """Check if text contains wake word"""
        if not self.wake_word_enabled:
            return True
        
        text_lower = text.lower()
        
        # Check English wake word
        if self.wake_word_en in text_lower:
            # Remove wake word from text
            text = text_lower.replace(self.wake_word_en, '').strip()
            return text if text else True
        
        # Check Urdu wake word
        if self.wake_word_ur in text:
            text = text.replace(self.wake_word_ur, '').strip()
            return text if text else True
        
        return False
    
    def listen(self, wait_for_wake_word=False):
        """
        Listen to microphone and convert speech to text
        Returns: (text, language) or (None, None)
        """
        with sr.Microphone() as source:
            try:
                # Better noise adjustment for noisy environments
                if wait_for_wake_word:
                    # Shorter adjustment for wake word
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                else:
                    # Longer adjustment for commands in noisy environment
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                # Increase energy threshold for noisy environments
                # Higher = less sensitive to background noise
                self.recognizer.energy_threshold = max(self.recognizer.energy_threshold, 400)
                
                # Dynamic energy threshold for adaptive noise handling
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.dynamic_energy_adjustment_damping = 0.15
                self.recognizer.dynamic_energy_ratio = 1.5
                
                if wait_for_wake_word:
                    logger.info("Waiting for wake word...")
                    print(f"💤 Say '{self.wake_word_en}' or '{self.wake_word_ur}' to activate")
                else:
                    logger.info("Listening...")
                    print("🎤 بولیں / Listening...")
                
                # Listen with better parameters
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.listen_timeout if not wait_for_wake_word else None,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                logger.info("Recognizing...")
                print("🔄 سمجھ رہا ہوں / Recognizing...")
                
                # Try English first
                try:
                    text_en = self.recognizer.recognize_google(audio, language='en-US')
                    
                    # Check for wake word if enabled
                    if wait_for_wake_word:
                        wake_result = self.check_wake_word(text_en)
                        if not wake_result:
                            return None, None
                        if isinstance(wake_result, str):
                            text_en = wake_result
                    
                    detected_lang = self.detect_language(text_en)
                    
                    # If Urdu detected, try Urdu recognition
                    if detected_lang == 'ur':
                        try:
                            text_ur = self.recognizer.recognize_google(audio, language='ur-PK')
                            logger.info(f"Recognized (Urdu): {text_ur}")
                            print(f"✅ آپ نے کہا: {text_ur}")
                            return text_ur, 'ur'
                        except:
                            pass
                    
                    logger.info(f"Recognized (English): {text_en}")
                    print(f"✅ You said: {text_en}")
                    return text_en, 'en'
                
                except sr.UnknownValueError:
                    # Try Urdu if English fails
                    try:
                        text_ur = self.recognizer.recognize_google(audio, language='ur-PK')
                        
                        # Check wake word
                        if wait_for_wake_word:
                            wake_result = self.check_wake_word(text_ur)
                            if not wake_result:
                                return None, None
                            if isinstance(wake_result, str):
                                text_ur = wake_result
                        
                        logger.info(f"Recognized (Urdu): {text_ur}")
                        print(f"✅ آپ نے کہا: {text_ur}")
                        return text_ur, 'ur'
                    except:
                        logger.warning("Could not recognize speech - try speaking louder or clearer")
                        print("⚠️  Couldn't hear you clearly. Try again.")
                        return None, None
            
            except sr.WaitTimeoutError:
                if not wait_for_wake_word:
                    logger.debug("Listen timeout")
                return None, None
            
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                return None, None
            
            except Exception as e:
                logger.error(f"Unexpected error in speech recognition: {e}")
                return None, None
    
    def listen_for_wake_word(self):
        """Listen specifically for wake word"""
        return self.listen(wait_for_wake_word=True)
    
    def calibrate_microphone(self):
        """Calibrate microphone for better recognition"""
        with sr.Microphone() as source:
            print("🎤 Calibrating microphone... Please wait in silence.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Calibration complete!")
            logger.info("Microphone calibrated")
