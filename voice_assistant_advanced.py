#!/usr/bin/env python3
"""
Advanced Bilingual Voice Assistant (English + Urdu)
With wake word detection, threading, caching, advanced features, and GUI
"""

import os
import sys
import webbrowser
from datetime import datetime
import re
import signal
import tkinter as tk
import threading
import queue
import math
import time

# Import our modules
from voice_utils import (
    load_config, setup_logging, InternetChecker, 
    sanitize_filename, command_exists, ConversationHistory, TTSCache
)
from tts_engine import TTSEngine
from speech_recognition_module import SpeechRecognizer
from system_actions import SystemActions
from multimedia_actions import MultimediaActions
from context_manager import ContextManager
from browser_tab_manager import BrowserTabManager
from workflow_manager import WorkflowManager, WorkflowState
from desktop_app_detector import DesktopAppDetector

class VoiceAssistantGUI:
    """Beautiful animated GUI for the voice assistant"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant - وائس اسسٹنٹ")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a0a0a')
        
        # Animation state
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.animation_running = True
        self.wave_offset = 0
        self.glow_intensity = 0
        self.pulse_phase = 0
        
        # Colors
        self.bg_color = '#0a0a0a'
        self.accent_color = '#00ff88'
        self.speaking_color = '#ff0088'
        self.listening_color = '#0088ff'
        self.processing_color = '#ffaa00'
        self.idle_color = '#444444'
        
        # Message queue for thread-safe updates
        self.message_queue = queue.Queue()
        
        self.setup_ui()
        self.start_animation()
        self.process_message_queue()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="AI VOICE ASSISTANT",
            font=('Arial', 28, 'bold'),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="وائس اسسٹنٹ | Bilingual English + Urdu",
            font=('Arial', 14),
            bg=self.bg_color,
            fg='#888888'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Canvas for visualizer
        self.canvas = tk.Canvas(
            main_frame,
            width=450,
            height=450,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="💤 Initializing...",
            font=('Arial', 16, 'bold'),
            bg=self.bg_color,
            fg='#888888'
        )
        self.status_label.pack(pady=15)
        
        # Transcript area
        transcript_frame = tk.Frame(main_frame, bg=self.bg_color)
        transcript_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(
            transcript_frame,
            text="📝 Conversation History:",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg='#888888',
            anchor='w'
        ).pack(fill=tk.X)
        
        # Text widget with scrollbar
        text_scroll_frame = tk.Frame(transcript_frame, bg=self.bg_color)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.transcript = tk.Text(
            text_scroll_frame,
            height=6,
            bg='#1a1a1a',
            fg='#ffffff',
            font=('Consolas', 10),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.transcript.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_scroll_frame, command=self.transcript.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcript.config(yscrollcommand=scrollbar.set)
        
        # Info footer
        info_label = tk.Label(
            main_frame,
            text="🎤 Say 'alexa' or 'الیکسا' to activate | Press Ctrl+C in terminal to exit",
            font=('Arial', 9),
            bg=self.bg_color,
            fg='#666666'
        )
        info_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def draw_circular_visualizer(self):
        """Draw animated circular visualizer"""
        self.canvas.delete('all')
        
        cx, cy = 225, 225
        base_radius = 90
        num_points = 60
        
        # Determine state and colors
        if self.is_speaking:
            color = self.speaking_color
            glow_target = 1.0
            wave_amplitude = 50
        elif self.is_listening:
            color = self.listening_color
            glow_target = 0.8
            wave_amplitude = 30
        elif self.is_processing:
            color = self.processing_color
            glow_target = 0.6
            wave_amplitude = 20
        else:
            color = self.idle_color
            glow_target = 0.2
            wave_amplitude = 8
        
        # Smooth glow transition
        self.glow_intensity += (glow_target - self.glow_intensity) * 0.15
        
        # Draw glow rings
        for i in range(6):
            glow_radius = base_radius + 70 - i * 12
            alpha = int(self.glow_intensity * (60 - i * 10))
            glow_color = self._blend_color(color, alpha)
            
            self.canvas.create_oval(
                cx - glow_radius, cy - glow_radius,
                cx + glow_radius, cy + glow_radius,
                outline=glow_color,
                width=2
            )
        
        # Draw waveform
        points = []
        for i in range(num_points + 1):
            angle = (i / num_points) * 2 * math.pi
            
            wave = math.sin(angle * 5 + self.wave_offset) * wave_amplitude
            wave += math.sin(angle * 3 - self.wave_offset * 0.7) * wave_amplitude * 0.4
            pulse = math.sin(self.pulse_phase) * 15 * self.glow_intensity
            
            radius = base_radius + wave + pulse
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
        
        if len(points) > 1:
            self.canvas.create_line(points, fill=color, width=4, smooth=True)
        
        # Center circle
        center_radius = 35
        self.canvas.create_oval(
            cx - center_radius, cy - center_radius,
            cx + center_radius, cy + center_radius,
            fill=self.bg_color,
            outline=color,
            width=3
        )
        
        # Icon
        if self.is_speaking:
            icon = "🗣️"
        elif self.is_listening:
            icon = "🎤"
        elif self.is_processing:
            icon = "⚙️"
        else:
            icon = "💤"
        
        self.canvas.create_text(cx, cy, text=icon, font=('Arial', 28))
        
        self.wave_offset += 0.12
        self.pulse_phase += 0.06
    
    def _blend_color(self, hex_color, alpha):
        """Blend color with background"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        bg = 10
        r = int(bg + (r - bg) * (alpha / 255))
        g = int(bg + (g - bg) * (alpha / 255))
        b = int(bg + (b - bg) * (alpha / 255))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def start_animation(self):
        """Start animation loop"""
        def animate():
            while self.animation_running:
                try:
                    if self.root.winfo_exists():
                        self.draw_circular_visualizer()
                        time.sleep(0.033)  # ~30 FPS
                    else:
                        break
                except Exception as e:
                    # Handle any drawing errors silently
                    time.sleep(0.1)
                    continue
        
        threading.Thread(target=animate, daemon=True).start()
    
    def process_message_queue(self):
        """Process queued GUI updates"""
        try:
            while True:
                try:
                    func, args = self.message_queue.get_nowait()
                    func(*args)
                except Exception as e:
                    # Silently handle GUI update errors
                    pass
        except queue.Empty:
            pass
        
        if self.root.winfo_exists():
            self.root.after(50, self.process_message_queue)
    
    def queue_update(self, func, *args):
        """Queue a GUI update"""
        try:
            if self.root and self.root.winfo_exists():
                self.message_queue.put((func, args))
        except:
            pass
    
    def set_listening(self):
        """Set listening state"""
        self.is_listening = True
        self.is_speaking = False
        self.is_processing = False
        self.status_label.config(text="🎤 Listening...", fg=self.listening_color)
    
    def set_speaking(self, text=""):
        """Set speaking state"""
        self.is_listening = False
        self.is_speaking = True
        self.is_processing = False
        display_text = text[:40] + "..." if len(text) > 40 else text
        self.status_label.config(text=f"🗣️ {display_text}", fg=self.speaking_color)
    
    def set_processing(self):
        """Set processing state"""
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = True
        self.status_label.config(text="⚙️ Processing...", fg=self.processing_color)
    
    def set_idle(self):
        """Set idle state"""
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.status_label.config(text="💤 Waiting for wake word...", fg='#888888')
    
    def add_user_message(self, text, lang='en'):
        """Add user message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = "You" if lang == 'en' else "آپ"
            self.transcript.insert(tk.END, f"[{timestamp}] 👤 {prefix}: {text}\n", 'user')
            self.transcript.tag_config('user', foreground='#00ff88')
            self.transcript.see(tk.END)
        except:
            pass
    
    def add_assistant_message(self, text, lang='en'):
        """Add assistant message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.transcript.insert(tk.END, f"[{timestamp}] 🤖 Assistant: {text}\n", 'assistant')
            self.transcript.tag_config('assistant', foreground='#0088ff')
            self.transcript.see(tk.END)
        except:
            pass
    
    def add_system_message(self, text):
        """Add system message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.transcript.insert(tk.END, f"[{timestamp}] ℹ️  {text}\n", 'system')
            self.transcript.tag_config('system', foreground='#888888')
            self.transcript.see(tk.END)
        except:
            pass
    
    def cleanup(self):
        """Cleanup"""
        self.animation_running = False

class VoiceAssistant:
    def __init__(self, config_path='config.ini', gui=None):
        # GUI reference
        self.gui = gui
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        log_file = os.path.expanduser(
            self.config.get('Paths', 'log_file', 
                           fallback='~/.local/share/voice_assistant/assistant.log')
        )
        self.logger = setup_logging(log_file)
        self.logger.info("="*60)
        self.logger.info("Voice Assistant Starting...")
        self.logger.info("="*60)
        
        # Initialize components
        self.internet_checker = InternetChecker(
            cache_duration=self.config.getint('Advanced', 'internet_check_cache', fallback=30)
        )
        
        # TTS Cache
        cache_enabled = self.config.getboolean('Text-to-Speech', 'enable_tts_cache', fallback=True)
        if cache_enabled:
            cache_dir = os.path.expanduser(
                self.config.get('Paths', 'cache_dir', fallback='~/.cache/voice_assistant')
            )
            cache_days = self.config.getint('Text-to-Speech', 'cache_duration_days', fallback=7)
            self.tts_cache = TTSCache(cache_dir, cache_days)
            self.tts_cache.clear_old()  # Clean old cache on startup
        else:
            self.tts_cache = None
        
        # Initialize TTS Engine
        self.tts = TTSEngine(self.config, self.internet_checker, self.tts_cache)
        
        # Initialize Speech Recognizer
        self.speech_recognizer = SpeechRecognizer(self.config)
        
        # Initialize action modules
        self.system_actions = SystemActions(self.config)
        self.multimedia_actions = MultimediaActions(self.config)
        
        # Conversation history
        history_enabled = self.config.getboolean('General', 'enable_history', fallback=True)
        if history_enabled:
            max_items = self.config.getint('General', 'max_history_items', fallback=10)
            self.history = ConversationHistory(max_items)
        else:
            self.history = None
        
        # Context Manager - NEW!
        self.context = ContextManager()
        self.logger.info("Context manager initialized")
        
        # Browser Tab Manager - NEW!
        try:
            self.tab_manager = BrowserTabManager()
            self.logger.info("Browser tab manager initialized")
        except Exception as e:
            self.logger.warning(f"Tab manager initialization failed: {e}")
            self.tab_manager = None
        
        # Desktop App Detector - NEW!
        try:
            self.app_detector = DesktopAppDetector()
            self.logger.info("Desktop app detector initialized")
        except Exception as e:
            self.logger.warning(f"App detector initialization failed: {e}")
            self.app_detector = None
        
        # Workflow Manager - NEW!
        try:
            self.workflow = WorkflowManager(self.context, self.tab_manager)
            self.logger.info("Workflow manager initialized")
        except Exception as e:
            self.logger.warning(f"Workflow manager initialization failed: {e}")
            self.workflow = None
        
        # Running state
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
    
    def shutdown_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        print("\n\n👋 Shutting down gracefully...")
        self.running = False
        self.tts.shutdown()
        sys.exit(0)
    
    def speak(self, text, lang='en'):
        """Wrapper for TTS speak with GUI updates"""
        if self.gui:
            self.gui.queue_update(self.gui.set_speaking, text)
            self.gui.queue_update(self.gui.add_assistant_message, text, lang)
        
        # Use non-blocking speak in GUI mode to prevent hanging
        if self.gui:
            self.tts.speak(text, lang, block=False)
            # Wait for speech to finish in background
            threading.Thread(target=lambda: (
                self.tts.wait_until_done(),
                self.gui.queue_update(self.gui.set_idle) if self.gui else None
            ), daemon=True).start()
        else:
            # Terminal mode - blocking is fine
            self.tts.speak(text, lang, block=True)
    
    def speak_async(self, text, lang='en'):
        """Non-blocking speak"""
        self.tts.speak_async(text, lang)
    
    def detect_language(self, text):
        """Detect language of text"""
        return self.speech_recognizer.detect_language(text)
    
    def open_application(self, app_name):
        """Open applications with PID tracking"""
        apps = {
            # English
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'chromium': 'chromium-browser',
            'brave': 'brave-browser',
            'terminal': self.config.get('System', 'terminal', fallback='gnome-terminal'),
            'files': self.config.get('System', 'file_manager', fallback='nautilus'),
            'file manager': self.config.get('System', 'file_manager', fallback='nautilus'),
            'calculator': 'gnome-calculator',
            'text editor': self.config.get('System', 'text_editor', fallback='gedit'),
            'notepad': self.config.get('System', 'text_editor', fallback='gedit'),
            'settings': 'gnome-control-center',
            'music': self.config.get('System', 'music_player', fallback='rhythmbox'),
            'videos': self.config.get('System', 'video_player', fallback='totem'),
            'code': 'code',
            'vs code': 'code',
            
            # Urdu
            'فائرفاکس': 'firefox',
            'کروم': 'google-chrome',
            'ٹرمینل': self.config.get('System', 'terminal', fallback='gnome-terminal'),
            'فائلز': self.config.get('System', 'file_manager', fallback='nautilus'),
            'کیلکولیٹر': 'gnome-calculator',
        }
        
        app_name_lower = app_name.lower()
        
        for key, command in apps.items():
            if key in app_name_lower:
                if command_exists(command.split()[0]):
                    try:
                        import subprocess
                        # Start process and get PID
                        process = subprocess.Popen(command.split())
                        pid = process.pid
                        
                        # Track in context manager
                        self.context.track_opened_app(key, command, pid)
                        
                        lang = self.detect_language(key)
                        msg = f"{key} کھول رہا ہوں" if lang == 'ur' else f"Opening {key}"
                        self.speak(msg, lang)
                        
                        # Add to context history
                        self.context.add_to_history(
                            f"open {key}",
                            f"opened {key}",
                            {'app': key, 'action': 'open'}
                        )
                        
                        return True
                    except Exception as e:
                        self.logger.error(f"Error opening {key}: {e}")
                
                lang = self.detect_language(key)
                msg = f"معذرت، {key} انسٹال نہیں ہے" if lang == 'ur' else f"Sorry, {key} is not installed"
                self.speak(msg, lang)
                return False
        
        lang = self.detect_language(app_name)
        msg = "معذرت، مجھے یہ ایپلیکیشن کھولنا نہیں آتا" if lang == 'ur' else "Sorry, I don't know how to open that"
        self.speak(msg, lang)
        return False
    
    def search_web(self, query):
        """Search the web"""
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        
        lang = self.detect_language(query)
        msg = f"{query} تلاش کر رہا ہوں" if lang == 'ur' else f"Searching for {query}"
        self.speak(msg, lang)
    
    def get_time(self, lang='en'):
        """Get current time"""
        current_time = datetime.now().strftime("%I:%M %p")
        
        msg = f"وقت {current_time} بج رہے ہیں" if lang == 'ur' else f"The time is {current_time}"
        self.speak(msg, lang)
    
    def get_date(self, lang='en'):
        """Get current date"""
        current_date = datetime.now().strftime("%B %d, %Y")
        day_name = datetime.now().strftime("%A")
        
        msg = f"آج {day_name} ہے، تاریخ {current_date} ہے" if lang == 'ur' else f"Today is {day_name}, {current_date}"
        self.speak(msg, lang)
    
    def process_command(self, command, lang='en'):
        """Process and execute commands with context awareness"""
        if not command:
            return True
        
        command_lower = command.lower()
        
        # Resolve context references ("it", "that", etc.)
        command_resolved = self.context.resolve_reference(command_lower)
        
        # Log what we're processing
        self.logger.info(f"Processing: '{command}' → Resolved: '{command_resolved}'")
        
        # Owner name query
        if any(phrase in command_lower for phrase in [
            'my name', 'what is my name', 'who am i',
            'your owner', 'owner name', 'who is your owner',
            'میرا نام', 'مالک کا نام'
        ]):
            msg = "آپ کا نام مسٹر امان ہے" if lang == 'ur' else "Your name is Mr Amaan. You are my owner."
            self.speak(msg, lang)
            return True
        
        # Greeting with name
        elif any(phrase in command_lower for phrase in [
            'hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon',
            'السلام علیکم', 'ہیلو'
        ]):
            from datetime import datetime
            hour = datetime.now().hour
            
            if hour < 12:
                greeting = "صبح بخیر" if lang == 'ur' else "Good morning"
            elif hour < 17:
                greeting = "دوپہر بخیر" if lang == 'ur' else "Good afternoon"
            else:
                greeting = "شام بخیر" if lang == 'ur' else "Good evening"
            
            msg = f"{greeting} مسٹر امان! میں آپ کی کیسے مدد کر سکتا ہوں?" if lang == 'ur' else f"{greeting} Mr Amaan! How can I help you?"
            self.speak(msg, lang)
            return True
        
        # =====================================================================
        # WORKFLOW STATE HANDLING - Check this FIRST
        # =====================================================================
        
        # If in profile selection mode, handle profile choice
        if self.workflow and self.workflow.state == WorkflowState.PROFILE_SELECTION:
            success, message = self.workflow.handle_profile_selection(command_lower)
            self.speak(message, lang)
            return True
        
        # =====================================================================
        # APP DETECTION COMMANDS
        # =====================================================================
        
        # List running apps
        elif 'what' in command_lower and any(word in command_lower for word in ['app', 'running', 'open', 'program']):
            if self.app_detector:
                summary = self.app_detector.get_app_summary()
                self.speak(summary, lang)
            else:
                self.speak("App detector not available. Install wmctrl.", lang)
            return True
        
        # Count specific app instances
        elif 'how many' in command_lower:
            if self.app_detector:
                for app_name in ['chrome', 'firefox', 'terminal', 'code', 'files', 'window']:
                    if app_name in command_lower:
                        if app_name == 'window':
                            windows = self.app_detector.get_all_windows()
                            count = len(windows)
                            msg = f"{count} window{'s' if count != 1 else ''} open"
                        else:
                            count = self.app_detector.count_app_instances(app_name)
                            msg = f"{count} {app_name} instance{'s' if count != 1 else ''} running"
                        self.speak(msg, lang)
                        return True
            else:
                self.speak("App detector not available", lang)
            return True
        
        # =====================================================================
        # CHROME WITH PROFILE - Must come BEFORE generic open
        # =====================================================================
        
        # Open Chrome with or without profile
        elif 'chrome' in command_lower and ('open' in command_lower or 'کھولو' in command_lower):
            # Extract profile if mentioned
            profile = None
            if 'profile' in command_lower or 'amaan' in command_lower or 'work' in command_lower:
                if 'profile 1' in command_lower or 'amaan' in command_lower or 'profile1' in command_lower:
                    profile = 'profile 1'
                elif 'profile 2' in command_lower or 'work' in command_lower or 'profile2' in command_lower:
                    profile = 'profile 2'
                elif 'default' in command_lower or 'me' in command_lower:
                    profile = 'default'
            
            if self.workflow:
                success, message = self.workflow.handle_browser_opening('chrome', profile)
                self.speak(message, lang)
                # Track in context
                self.context.track_opened_app('chrome', 'google-chrome')
            else:
                # Fallback
                self.open_application('chrome')
            return True
        
        # =====================================================================
        # SEARCH COMMANDS - Must come BEFORE generic open
        # =====================================================================
        
        # Search on current platform
        elif 'search for' in command_lower or 'search' in command_lower and 'for' in command_lower:
            # Extract query
            query = None
            if 'search for' in command_lower:
                query = command_lower.split('search for', 1)[1].strip()
            
            if query and self.workflow:
                success, message = self.workflow.handle_search_query(query)
                self.speak(message, lang)
            elif query:
                self.search_web(query)
            else:
                self.speak("What should I search for?", lang)
            return True
        
        # =====================================================================
        # WEBSITE OPENING - Must come BEFORE generic open
        # =====================================================================
        
        # Open specific websites
        elif any(site in command_lower for site in ['youtube', 'gmail', 'facebook', 'twitter', 'github', 'reddit', 'netflix']):
            for site in ['youtube', 'gmail', 'facebook', 'twitter', 'github', 'reddit', 'netflix']:
                if site in command_lower:
                    if self.workflow:
                        success, message = self.workflow.handle_website_opening(site)
                        self.speak(message, lang)
                    else:
                        from constants import WEBSITE_URLS
                        url = WEBSITE_URLS.get(site, f'https://{site}.com')
                        webbrowser.open(url)
                        self.speak(f"Opening {site}", lang)
                    return True
        
        # Open application / website
        elif 'open' in command_resolved or 'کھولو' in command_resolved or 'کھول' in command_resolved:
            app_name = command_resolved
            for word in ['open', 'کھولو', 'کھول', 'the', 'a']:
                app_name = app_name.replace(word, '')
            app_name = app_name.strip()
            
            # Check if it's a website (youtube, github, etc.)
            websites = ['youtube', 'gmail', 'github', 'facebook', 'twitter', 'reddit', 'stackoverflow']
            is_website = any(site in app_name.lower() for site in websites)
            
            if is_website and self.tab_manager:
                # Check if tab is already open
                site_name = next((site for site in websites if site in app_name.lower()), None)
                if site_name:
                    existing_tab = self.tab_manager.find_tab_by_website(site_name)
                    
                    if existing_tab:
                        # Option B & C: Ask + Notify
                        msg = f"{site_name.capitalize()} is already open. Switch to it or open new tab?" if lang == 'en' else f"{site_name} پہلے سے کھلا ہے۔ اس پر جائیں یا نیا ٹیب کھولیں?"
                        self.speak(msg, lang)
                        
                        # Wait for response
                        if self.gui:
                            self.gui.queue_update(self.gui.set_listening)
                        
                        response, response_lang = self.speech_recognizer.listen()
                        
                        if response:
                            response_lower = response.lower()
                            
                            if any(word in response_lower for word in ['switch', 'go', 'yes', 'ہاں', 'جاؤ']):
                                # Switch to existing tab
                                success, message = self.tab_manager.switch_to_tab(existing_tab)
                                self.speak(message if lang == 'en' else f"{site_name} پر جا رہے ہیں", lang)
                                return True
                            elif any(word in response_lower for word in ['new', 'open', 'نیا', 'کھولو']):
                                # Open new tab - continue to normal open
                                msg = f"Opening new {site_name} tab" if lang == 'en' else f"نیا {site_name} ٹیب کھول رہے ہیں"
                                self.speak(msg, lang)
                            else:
                                # Unclear response, default to switch
                                success, message = self.tab_manager.switch_to_tab(existing_tab)
                                self.speak(message, lang)
                                return True
                    else:
                        # Not open, notify and open
                        msg = f"{site_name.capitalize()} is not open. Opening it now." if lang == 'en' else f"{site_name} کھلا نہیں ہے۔ کھول رہے ہیں"
                        self.speak(msg, lang)
            
            # Normal app opening
            self.open_application(app_name)
        
        # Close application - NEW!
        elif any(word in command_resolved for word in ['close', 'بند']):
            # Extract app name or use context
            app_to_close = self.context.extract_app_name(command_resolved)
            success, message = self.context.close_app(app_to_close)
            
            self.speak(message if lang == 'en' else f"بند کر دیا", lang)
            
            if success:
                self.context.add_to_history(
                    command,
                    f"closed {app_to_close or 'app'}",
                    {'action': 'close', 'app': app_to_close}
                )
        
        # Chrome/Browser profile selection - NEW!
        elif any(word in command_resolved for word in ['profile', 'پروفائل']) and self.context.is_browser_task():
            # Extract profile name/number
            import re
            
            # Try to find profile name/number
            if 'profile 1' in command_resolved or 'امان' in command_resolved or 'amaan' in command_resolved:
                profile = 'amaan'
            elif 'profile 2' in command_resolved or 'me' in command_resolved:
                profile = 'me'
            elif match := re.search(r'profile (\d+)', command_resolved):
                profile = match.group(1)
            else:
                # Default to asking
                self.speak("Which profile? Say 'Amaan' or 'me'", lang)
                return True
            
            # Open Chrome with specific profile
            try:
                import subprocess
                chrome_cmd = self.context.get_chrome_profile_command(profile)
                process = subprocess.Popen(chrome_cmd.split())
                self.context.track_opened_app('chrome', chrome_cmd, process.pid)
                
                msg = f"پروفائل {profile} کے ساتھ کروم کھول رہا ہوں" if lang == 'ur' else f"Opening Chrome with {profile} profile"
                self.speak(msg, lang)
            except Exception as e:
                self.speak("Could not open profile", lang)
                print(f"Profile error: {e}")
        
        # Go to website - NEW!
        elif any(word in command_resolved for word in ['go to', 'open', 'navigate']) and \
             any(site in command_resolved for site in ['youtube', 'gmail', 'google', 'facebook', '.com', 'www']):
            # Extract website
            websites = {
                'youtube': 'https://youtube.com',
                'gmail': 'https://gmail.com',
                'google': 'https://google.com',
                'facebook': 'https://facebook.com',
                'twitter': 'https://twitter.com',
                'github': 'https://github.com'
            }
            
            url = None
            for site, site_url in websites.items():
                if site in command_resolved:
                    url = site_url
                    break
            
            if url:
                success, message = self.context.open_url_in_browser(url)
                self.speak(message if lang == 'en' else f"{url} کھول رہا ہوں", lang)
            else:
                # Try to extract custom URL
                import re
                url_match = re.search(r'(https?://\S+|www\.\S+|\S+\.com)', command_resolved)
                if url_match:
                    url = url_match.group(0)
                    if not url.startswith('http'):
                        url = 'https://' + url
                    success, message = self.context.open_url_in_browser(url)
                    self.speak(message, lang)
        
        # Exit assistant (specific command)
        # Make sure "turn off" doesn't conflict with "turn off wifi/bluetooth"
        exit_phrases = [
            'exit', 'quit', 'stop', 'shutdown assistant', 
            'goodbye', 'bye', 'see you', 'stop alexa', 'exit alexa', 'goodbye alexa',
            'خدا حافظ', 'رخصت'
        ]
        
        # Check for exit, but exclude if it's about turning off a specific thing
        is_exit_command = any(phrase in command_lower for phrase in exit_phrases)
        
        # Special handling for "turn off" - only exit if not followed by wifi/bluetooth/etc
        if 'turn off' in command_lower or 'بند کرو' in command_lower:
            # Check if it's turning off a specific feature
            feature_words = ['wifi', 'bluetooth', 'wifi', 'وائی فائی', 'بلوٹوتھ', 'volume', 'brightness']
            is_feature_command = any(feature in command_lower for feature in feature_words)
            
            if not is_feature_command:
                # Just "turn off" without specifying what = exit
                is_exit_command = True
        
        if is_exit_command:
            msg = "خدا حافظ! اچھا دن گزرے!" if lang == 'ur' else "Goodbye! Have a great day!"
            self.speak(msg, lang)
            
            # Set running to False to exit main loop
            self.running = False
            return False
        
        # Web search
        elif 'search' in command_lower or 'google' in command_lower or 'تلاش' in command_lower:
            query = command_lower
            for word in ['search', 'google', 'for', 'تلاش', 'کرو', 'گوگل']:
                query = query.replace(word, '')
            query = query.strip()
            if query:
                self.search_web(query)
            else:
                msg = "کیا تلاش کروں؟" if lang == 'ur' else "What should I search for?"
                self.speak(msg, lang)
        
        # Tab Management Commands - NEW!
        elif self.tab_manager and any(phrase in command_lower for phrase in [
            'what tabs', 'list tabs', 'show tabs', 'tabs open',
            'ٹیب کیا ہیں', 'ٹیبز دکھاؤ'
        ]):
            # List all open tabs
            tabs = self.tab_manager.get_all_tabs()
            
            if tabs:
                if len(tabs) == 1:
                    msg = f"You have 1 tab open: {tabs[0]['title']}" if lang == 'en' else f"ایک ٹیب کھلا ہے: {tabs[0]['title']}"
                else:
                    tab_names = [tab['title'] for tab in tabs[:5]]  # First 5
                    if lang == 'en':
                        msg = f"You have {len(tabs)} tabs open: {', '.join(tab_names)}"
                        if len(tabs) > 5:
                            msg += f", and {len(tabs) - 5} more"
                    else:
                        msg = f"{len(tabs)} ٹیبز کھلے ہیں"
                self.speak(msg, lang)
            else:
                msg = "No browser tabs are open" if lang == 'en' else "کوئی ٹیب کھلا نہیں ہے"
                self.speak(msg, lang)
        
        elif self.tab_manager and any(phrase in command_lower for phrase in [
            'switch to', 'go to', 'open tab',
            'جاؤ', 'کھولو ٹیب'
        ]):
            # Switch to specific tab
            # Extract website name
            websites = ['youtube', 'gmail', 'github', 'facebook', 'twitter', 'reddit']
            site_name = None
            for site in websites:
                if site in command_lower:
                    site_name = site
                    break
            
            if site_name:
                tab = self.tab_manager.find_tab_by_website(site_name)
                if tab:
                    success, message = self.tab_manager.switch_to_tab(tab)
                    self.speak(message if lang == 'en' else f"{site_name} پر جا رہے ہیں", lang)
                else:
                    msg = f"{site_name.capitalize()} is not open" if lang == 'en' else f"{site_name} کھلا نہیں ہے"
                    self.speak(msg, lang)
            else:
                msg = "Which tab do you want to switch to?" if lang == 'en' else "کس ٹیب پر جانا چاہتے ہیں؟"
                self.speak(msg, lang)
        
        elif self.tab_manager and any(phrase in command_lower for phrase in [
            'close tab', 'close youtube', 'close github', 'close gmail',
            'ٹیب بند', 'بند کرو ٹیب'
        ]):
            # Close specific tab
            websites = ['youtube', 'gmail', 'github', 'facebook', 'twitter', 'reddit']
            site_name = None
            for site in websites:
                if site in command_lower:
                    site_name = site
                    break
            
            if site_name:
                tab = self.tab_manager.find_tab_by_website(site_name)
                if tab:
                    success, message = self.tab_manager.close_tab(tab)
                    self.speak(message if lang == 'en' else f"{site_name} بند کر دیا", lang)
                else:
                    msg = f"{site_name.capitalize()} tab is not open" if lang == 'en' else f"{site_name} ٹیب کھلا نہیں ہے"
                    self.speak(msg, lang)
            else:
                msg = "Which tab do you want to close?" if lang == 'en' else "کون سا ٹیب بند کرنا ہے؟"
                self.speak(msg, lang)
        
        elif self.tab_manager and any(phrase in command_lower for phrase in [
            'is youtube open', 'is github open', 'is gmail open',
            'کیا کھلا ہے'
        ]):
            # Check if specific site is open
            websites = ['youtube', 'gmail', 'github', 'facebook', 'twitter', 'reddit']
            site_name = None
            for site in websites:
                if site in command_lower:
                    site_name = site
                    break
            
            if site_name:
                is_open = self.tab_manager.is_website_open(site_name)
                if is_open:
                    msg = f"Yes, {site_name.capitalize()} is open" if lang == 'en' else f"ہاں، {site_name} کھلا ہے"
                else:
                    msg = f"No, {site_name.capitalize()} is not open" if lang == 'en' else f"نہیں، {site_name} کھلا نہیں ہے"
                self.speak(msg, lang)
            else:
                msg = "Which website are you asking about?" if lang == 'en' else "کس ویب سائٹ کے بارے میں پوچھ رہے ہیں؟"
                self.speak(msg, lang)
        
        elif self.tab_manager and any(phrase in command_lower for phrase in [
            'how many tabs', 'tab count', 'count tabs',
            'کتنے ٹیب'
        ]):
            # Get tab count
            count = self.tab_manager.get_tab_count()
            if count == 0:
                msg = "No tabs are open" if lang == 'en' else "کوئی ٹیب کھلا نہیں ہے"
            elif count == 1:
                msg = "You have 1 tab open" if lang == 'en' else "ایک ٹیب کھلا ہے"
            else:
                msg = f"You have {count} tabs open" if lang == 'en' else f"{count} ٹیب کھلے ہیں"
            self.speak(msg, lang)
        
        # Time and date
        elif 'time' in command_lower or 'وقت' in command_lower:
            self.get_time(lang)
        elif 'date' in command_lower or 'تاریخ' in command_lower:
            self.get_date(lang)
        
        # System actions - Brightness
        elif 'brightness' in command_lower or 'روشنی' in command_lower:
            success, message = self.system_actions.control_brightness(command_lower)
            self.speak(message, lang)
        
        # WiFi control
        elif 'wifi' in command_lower or 'وائی فائی' in command_lower:
            success, message = self.system_actions.control_wifi(command_lower)
            self.speak(message, lang)
        
        # Bluetooth
        elif 'bluetooth' in command_lower or 'بلوٹوتھ' in command_lower:
            success, message = self.system_actions.control_bluetooth(command_lower)
            self.speak(message, lang)
        
        # Battery info
        elif 'battery' in command_lower or 'بیٹری' in command_lower:
            success, message = self.system_actions.get_battery_info()
            self.speak(message, lang)
        
        # Disk space
        elif 'disk' in command_lower or 'space' in command_lower or 'storage' in command_lower:
            success, message = self.system_actions.get_disk_space()
            self.speak(message, lang)
        
        # Memory info
        elif 'memory' in command_lower or 'ram' in command_lower:
            success, message = self.system_actions.get_memory_info()
            self.speak(message, lang)
        
        # Lock screen
        elif 'lock' in command_lower and 'screen' in command_lower:
            success, message = self.system_actions.lock_screen()
            self.speak(message, lang)
        
        # Power actions
        elif any(word in command_lower for word in ['shutdown', 'restart', 'reboot', 'sleep', 'logout']):
            confirm = self.config.getboolean('System', 'confirm_shutdown', fallback=True)
            success, message = self.system_actions.power_action(command_lower, confirm)
            self.speak(message, lang)
        
        # Multimedia - Music control
        elif 'play' in command_lower and 'music' not in command_lower:
            if 'pause' in command_lower:
                success, message = self.multimedia_actions.play_pause()
            else:
                success, message = self.multimedia_actions.play()
            self.speak(message, lang)
        
        elif 'pause' in command_lower:
            success, message = self.multimedia_actions.pause()
            self.speak(message, lang)
        
        elif 'stop' in command_lower and 'music' in command_lower:
            success, message = self.multimedia_actions.stop()
            self.speak(message, lang)
        
        elif 'next' in command_lower or 'skip' in command_lower:
            success, message = self.multimedia_actions.next_track()
            self.speak(message, lang)
        
        elif 'previous' in command_lower or 'back' in command_lower:
            success, message = self.multimedia_actions.previous_track()
            self.speak(message, lang)
        
        elif 'what' in command_lower and ('playing' in command_lower or 'song' in command_lower):
            success, message = self.multimedia_actions.get_current_track()
            self.speak(message, lang)
        
        elif 'play music' in command_lower or 'موسیقی چلاؤ' in command_lower:
            success, message = self.multimedia_actions.play_music_from_directory()
            self.speak(message, lang)
        
        # Volume control
        elif 'volume' in command_lower or 'آواز' in command_lower:
            # Check for percentage
            match = re.search(r'(\d+)%?', command_lower)
            if match:
                percentage = int(match.group(1))
                success, message = self.multimedia_actions.control_volume_percentage(percentage)
                self.speak(message, lang)
            elif 'get' in command_lower or 'what' in command_lower or 'کتنی' in command_lower:
                success, message = self.multimedia_actions.get_volume()
                self.speak(message, lang)
        
        # Screenshot
        elif 'screenshot' in command_lower or 'سکرین شاٹ' in command_lower:
            success, message = self.multimedia_actions.take_screenshot()
            self.speak(message, lang)
        
        # Help
        elif 'help' in command_lower or 'what can you do' in command_lower or 'مدد' in command_lower:
            # Check workflow state for contextual help
            if self.workflow and self.workflow.state != WorkflowState.IDLE:
                help_msg = self.workflow.get_help_message()
                self.speak(help_msg, lang)
            elif lang == 'ur':
                help_text = """مسٹر امان، میں آپ کی مدد کر سکتا ہوں: ایپلیکیشنز کھولنے، ویب تلاش کرنے،
                وقت اور تاریخ بتانے، روشنی اور آواز کنٹرول کرنے، موسیقی چلانے،
                وائی فائی اور بلوٹوتھ کنٹرول کرنے، بیٹری اور سسٹم کی معلومات لینے میں۔
                نئی خصوصیات: کروم پروفائل کھولنا، چلنے والے ایپس دیکھنا، سیکوینشل کمانڈز۔"""
            else:
                help_text = """Hello Mr Amaan! I can help you with: opening apps, web search, time and date,
                brightness and volume control, music playback, WiFi and Bluetooth,
                battery info, system information, screenshots, and more!
                
                NEW Features: Open Chrome with profiles, see running apps, sequential workflows!
                Try: 'What apps are running?', 'Open Chrome with Profile 1', 'Search for Python'"""
            self.speak(help_text, lang)
        
        # Unknown command
        else:
            msg = "مجھے ابھی یہ کرنا نہیں آتا" if lang == 'ur' else "I'm not sure how to do that yet"
            self.speak(msg, lang)
        
        return True
    
    def run(self):
        """Main loop"""
        # If GUI mode, update GUI instead of printing
        if self.gui:
            self.gui.queue_update(self.gui.add_system_message, "🚀 Voice Assistant Starting...")
            
            if self.internet_checker.is_connected():
                self.gui.queue_update(self.gui.add_system_message, "✅ Internet: Connected")
            else:
                self.gui.queue_update(self.gui.add_system_message, "⚠️  Internet: Offline")
            
            self.gui.queue_update(self.gui.add_system_message, 
                                f"✅ TTS Cache: {'Enabled' if self.tts_cache else 'Disabled'}")
            
            wake_word_enabled = self.config.getboolean('Features', 'enable_wake_word', fallback=True)
            if wake_word_enabled:
                wake_word = self.config.get('General', 'wake_word', fallback='assistant')
                self.gui.queue_update(self.gui.add_system_message, f"✅ Wake Word: '{wake_word}'")
            
            self.gui.queue_update(self.gui.add_system_message, "✅ Assistant Ready!")
        else:
            # Terminal mode output
            print("\n" + "="*60)
            print("🤖 BILINGUAL VOICE ASSISTANT")
            print("   دو لسانی وائس اسسٹنٹ")
            print("="*60)
            
            print("\n📋 System Status:")
            if self.internet_checker.is_connected():
                print("✅ Internet: Connected")
            else:
                print("⚠️  Internet: Offline (Urdu TTS unavailable)")
            
            print(f"✅ TTS Cache: {'Enabled' if self.tts_cache else 'Disabled'}")
            print(f"✅ Conversation History: {'Enabled' if self.history else 'Disabled'}")
            
            wake_word_enabled = self.config.getboolean('Features', 'enable_wake_word', fallback=True)
            if wake_word_enabled:
                wake_word = self.config.get('General', 'wake_word', fallback='assistant')
                print(f"✅ Wake Word: Enabled ('{wake_word}')")
            else:
                print("⚠️  Wake Word: Disabled (always listening)")
            
            print("\n" + "="*60 + "\n")
        
        # Welcome message (silent in GUI mode to prevent early activation)
        if self.gui:
            # GUI mode - show text only
            self.gui.queue_update(self.gui.add_system_message, "🎉 Alexa Activated!")
            self.gui.queue_update(self.gui.add_system_message, "🎤 Say 'Alexa' or 'الیکسا' to start")
        else:
            # Terminal mode - speak welcome
            self.speak("الیکسا فعال ہو گئی", 'ur')
            self.speak("Alexa activated. How can I help you?", 'en')
        
        # Calibrate microphone
        if self.gui:
            self.gui.queue_update(self.gui.add_system_message, "🎤 Calibrating microphone...")
        self.speech_recognizer.calibrate_microphone()
        if self.gui:
            self.gui.queue_update(self.gui.add_system_message, "✅ Microphone calibrated!")
            self.gui.queue_update(self.gui.add_system_message, "✅ Ready to listen!")
        
        # Wait a moment for everything to settle
        import time
        time.sleep(0.5)  # Brief pause before starting
        
        # Get wake word setting
        wake_word_enabled = self.config.getboolean('Features', 'enable_wake_word', fallback=True)
        
        # Main loop
        while self.running:
            try:
                # Listen for wake word if enabled
                if wake_word_enabled:
                    if self.gui:
                        self.gui.queue_update(self.gui.set_idle)
                    
                    text, lang = self.speech_recognizer.listen_for_wake_word()
                    if not text:
                        continue
                    
                    # Wake word detected
                    if self.gui:
                        self.gui.queue_update(self.gui.add_system_message, "👂 Wake word detected!")
                    
                    self.speak_async("جی؟" if lang == 'ur' else "Yes?", lang or 'en')
                else:
                    # Always listening mode
                    if self.gui:
                        self.gui.queue_update(self.gui.set_listening)
                    
                    text, lang = self.speech_recognizer.listen()
                
                if text and lang:
                    # Add user message to GUI
                    if self.gui:
                        self.gui.queue_update(self.gui.add_user_message, text, lang)
                        self.gui.queue_update(self.gui.set_processing)
                    
                    # Process command
                    should_continue = self.process_command(text, lang)
                    
                    # Add to history
                    if self.history:
                        self.history.add(text, "Command executed", lang)
                    
                    if not should_continue:
                        break
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                break
            
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                # Use last known language or default to English
                error_lang = lang if 'lang' in locals() else 'en'
                if self.gui:
                    self.gui.queue_update(self.gui.add_system_message, f"❌ Error: {str(e)}")
                else:
                    print(f"Error: {e}")
                self.speak("معذرت، ایک خرابی ہوئی" if error_lang == 'ur' else "Sorry, an error occurred", error_lang)
        
        # Cleanup
        self.logger.info("Voice Assistant shutting down")
        if self.gui:
            self.gui.queue_update(self.gui.add_system_message, "👋 Shutting down...")
            # Give time for message to display
            import time
            time.sleep(1)
            # Close GUI if running
            try:
                self.gui.root.quit()
            except:
                pass
        self.tts.shutdown()
        
        if not self.gui:
            print("\n👋 Goodbye!\n")

def main():
    """Entry point - supports both GUI and terminal modes"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bilingual Voice Assistant')
    parser.add_argument('--no-gui', action='store_true', help='Run in terminal mode without GUI')
    args = parser.parse_args()
    
    # Check config file
    config_path = 'config.ini'
    if not os.path.exists(config_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.ini')
    
    if args.no_gui:
        # Terminal mode
        print("Starting in terminal mode...")
        assistant = VoiceAssistant(config_path, gui=None)
        assistant.run()
    else:
        # GUI mode
        print("🎨 Starting GUI mode...")
        print("📱 Creating window...")
        
        root = tk.Tk()
        gui = VoiceAssistantGUI(root)
        
        print("🤖 Initializing assistant...")
        assistant = VoiceAssistant(config_path, gui=gui)
        
        print("✅ GUI ready! Window should appear now...")
        
        # Start assistant in background - non-blocking
        def start_assistant_background():
            try:
                print("🎤 Starting voice recognition...")
                assistant.run()
            except Exception as e:
                print(f"❌ Assistant error: {e}")
                import traceback
                traceback.print_exc()
        
        # Start assistant after GUI is ready
        root.after(500, lambda: threading.Thread(target=start_assistant_background, daemon=True).start())
        
        # Handle window close
        def on_closing():
            print("\n👋 Closing assistant...")
            assistant.running = False
            try:
                assistant.tts.shutdown()
            except:
                pass
            gui.cleanup()
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        try:
            print("🎬 Starting GUI loop...")
            root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted!")
            on_closing()
        
        print("\n✅ Exited cleanly")

if __name__ == "__main__":
    main()
