"""
Context Manager - Gives the assistant memory and context awareness
Tracks: opened apps, conversation history, current tasks, entities mentioned
"""

import subprocess
import psutil
import time
from datetime import datetime

class ContextManager:
    """Manages conversation context and application state"""
    
    def __init__(self):
        # Track opened applications
        self.opened_apps = []  # List of {name, command, pid, timestamp}
        
        # Conversation history with context
        self.conversation_history = []  # Last N commands with context
        self.max_history = 10
        
        # Current context
        self.last_app_mentioned = None
        self.last_action = None
        self.last_entity = None  # Last mentioned thing (website, file, etc.)
        
        # Active tasks
        self.current_task = None  # Multi-step task tracking
        
    def add_to_history(self, user_command, assistant_action, entities=None):
        """Add command to history with context"""
        entry = {
            'timestamp': datetime.now(),
            'user_command': user_command,
            'assistant_action': assistant_action,
            'entities': entities or {},
            'app_mentioned': self.last_app_mentioned
        }
        
        self.conversation_history.append(entry)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def track_opened_app(self, app_name, command, pid=None):
        """Track an opened application"""
        app_info = {
            'name': app_name,
            'command': command,
            'pid': pid,
            'timestamp': datetime.now()
        }
        
        self.opened_apps.append(app_info)
        self.last_app_mentioned = app_name
        
        print(f"📝 Tracked: {app_name} (PID: {pid})")
    
    def close_app(self, app_identifier=None):
        """
        Close application by name or use last mentioned
        Returns: (success, message)
        """
        # Determine which app to close
        if app_identifier:
            # Specific app mentioned
            target_app = app_identifier.lower()
        elif self.last_app_mentioned:
            # Use context: "close it", "close that"
            target_app = self.last_app_mentioned.lower()
        else:
            return False, "I don't know which app to close"
        
        # Try to find and close the app
        closed = False
        
        # Method 1: Close from our tracked apps
        for app in reversed(self.opened_apps):  # Start with most recent
            if target_app in app['name'].lower():
                try:
                    if app['pid']:
                        # Kill by PID
                        process = psutil.Process(app['pid'])
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful termination fails
                            process.kill()
                        closed = True
                    else:
                        # Kill by name
                        subprocess.run(['pkill', '-f', app['command']], timeout=2)
                        closed = True
                    
                    self.opened_apps.remove(app)
                    print(f"✅ Closed tracked app: {app['name']}")
                    return True, f"Closed {app['name']}"
                except psutil.NoSuchProcess:
                    # Process already closed
                    self.opened_apps.remove(app)
                    return True, f"{app['name']} was already closed"
                except Exception as e:
                    print(f"⚠️  Error closing {app['name']}: {e}")
                    pass
        
        # Method 2: Find and close by process name
        if not closed:
            try:
                # Common app name mappings
                process_names = {
                    'chrome': 'chrome',
                    'firefox': 'firefox',
                    'terminal': 'gnome-terminal',
                    'calculator': 'gnome-calculator',
                    'files': 'nautilus',
                    'code': 'code',
                    'vscode': 'code'
                }
                
                process_name = process_names.get(target_app, target_app)
                
                # Find and kill processes
                killed_count = 0
                for proc in psutil.process_iter(['name', 'cmdline']):
                    try:
                        if process_name in proc.info['name'].lower() or \
                           any(process_name in cmd.lower() for cmd in (proc.info['cmdline'] or [])):
                            proc.terminate()
                            killed_count += 1
                    except:
                        pass
                
                if killed_count > 0:
                    time.sleep(0.5)  # Wait for graceful shutdown
                    return True, f"Closed {target_app} ({killed_count} instance{'s' if killed_count > 1 else ''})"
                else:
                    return False, f"{target_app} is not running"
            except Exception as e:
                return False, f"Could not close {target_app}: {str(e)}"
        
        return False, f"Could not close {target_app}"
    
    def resolve_reference(self, text):
        """
        Resolve pronouns and references to actual entities
        "it" → last app mentioned
        "that" → last app mentioned
        "the app" → last app mentioned
        """
        text_lower = text.lower()
        
        # Replace pronouns with actual references
        if any(word in text_lower for word in ['it', 'that', 'this', 'the app', 'the application']):
            if self.last_app_mentioned:
                # Replace references
                replacements = ['it', 'that', 'this', 'the app', 'the application']
                for ref in replacements:
                    text_lower = text_lower.replace(ref, self.last_app_mentioned.lower())
        
        return text_lower
    
    def extract_app_name(self, command):
        """Extract app name from command"""
        command_lower = command.lower()
        
        # List of known apps
        known_apps = [
            'chrome', 'firefox', 'terminal', 'calculator', 'files',
            'code', 'vscode', 'settings', 'music', 'videos',
            'chromium', 'brave', 'nautilus', 'gedit'
        ]
        
        for app in known_apps:
            if app in command_lower:
                return app
        
        return None
    
    def get_context_info(self):
        """Get current context information"""
        info = {
            'last_app': self.last_app_mentioned,
            'opened_apps_count': len(self.opened_apps),
            'recent_commands': len(self.conversation_history),
            'current_task': self.current_task
        }
        return info
    
    def set_task(self, task_name):
        """Set current multi-step task"""
        self.current_task = task_name
    
    def clear_task(self):
        """Clear current task"""
        self.current_task = None
    
    def is_browser_task(self):
        """Check if current task involves a browser"""
        if self.last_app_mentioned:
            return self.last_app_mentioned.lower() in ['chrome', 'firefox', 'chromium', 'brave']
        return False
    
    def get_chrome_profile_command(self, profile_name):
        """Get Chrome command with specific profile"""
        # Map common profile names
        profiles = {
            'me': 'Default',
            'amaan': 'Profile 1',
            'profile 1': 'Profile 1',
            'profile 2': 'Profile 2',
            'work': 'Profile 2',
            'personal': 'Default',
            '1': 'Profile 1',
            '2': 'Profile 2'
        }
        
        profile_dir = profiles.get(profile_name.lower(), 'Default')
        return f'google-chrome --profile-directory="{profile_dir}"'
    
    def open_url_in_browser(self, url):
        """Open URL in last opened browser"""
        if not self.last_app_mentioned:
            return False, "No browser is open"
        
        try:
            import subprocess
            import webbrowser
            
            # Just use default browser opener
            webbrowser.open(url)
            return True, f"Opening {url}"
        except Exception as e:
            return False, f"Could not open URL: {str(e)}"
    
    def get_recent_history(self, n=3):
        """Get last N commands for context"""
        return self.conversation_history[-n:] if self.conversation_history else []
