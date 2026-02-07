# Code Snippets to Add to voice_assistant_advanced.py

## Add these AFTER line 600 (after greetings section) in process_command() method:

```python
        # =====================================================================
        # WORKFLOW-AWARE COMMANDS - Check workflow state first
        # =====================================================================
        
        # If in profile selection mode, handle profile choice
        if self.workflow and self.workflow.state == WorkflowState.PROFILE_SELECTION:
            success, message = self.workflow.handle_profile_selection(command_lower)
            self.speak(message, lang)
            return True
        
        # =====================================================================
        # NEW: DESKTOP APP DETECTION
        # =====================================================================
        
        # List running apps
        elif 'what' in command_lower and any(word in command_lower for word in ['app', 'running', 'open']):
            if 'running' in command_lower or 'open' in command_lower:
                if self.app_detector:
                    summary = self.app_detector.get_app_summary()
                    self.speak(summary, lang)
                else:
                    self.speak("App detector not available", lang)
                return True
        
        # Count specific app instances
        elif 'how many' in command_lower and any(app in command_lower for app in ['chrome', 'firefox', 'terminal', 'window']):
            if self.app_detector:
                # Extract app name
                for app_name in ['chrome', 'firefox', 'terminal', 'code', 'files']:
                    if app_name in command_lower:
                        count = self.app_detector.count_app_instances(app_name)
                        msg = f"{count} {app_name} instance{'s' if count != 1 else ''} running"
                        self.speak(msg, lang)
                        return True
        
        # =====================================================================
        # ENHANCED: CHROME WITH WORKFLOW SUPPORT
        # =====================================================================
        
        # Open Chrome with profile support
        elif 'chrome' in command_lower and ('open' in command_lower or 'کھولو' in command_lower):
            # Check if asking for specific profile
            profile = None
            if 'profile' in command_lower or 'amaan' in command_lower:
                if 'profile 1' in command_lower or 'amaan' in command_lower or ' 1' in command_lower:
                    profile = 'profile 1'
                elif 'profile 2' in command_lower or 'work' in command_lower or ' 2' in command_lower:
                    profile = 'profile 2'
            
            if self.workflow:
                success, message = self.workflow.handle_browser_opening('chrome', profile)
            else:
                # Fallback to old method
                success, message = self.open_application('chrome')
            
            self.speak(message, lang)
            return True
        
        # =====================================================================
        # ENHANCED: WEBSITE OPENING WITH WORKFLOW
        # =====================================================================
        
        # Smart website opening
        elif any(site in command_lower for site in ['youtube', 'gmail', 'google', 'facebook', 'github', 'reddit', 'netflix', 'twitter']):
            # Find which site
            for site in ['youtube', 'gmail', 'google', 'facebook', 'github', 'reddit', 'netflix', 'twitter']:
                if site in command_lower:
                    if self.workflow:
                        success, message = self.workflow.handle_website_opening(site)
                    else:
                        # Fallback to old method
                        from constants import WEBSITE_URLS
                        url = WEBSITE_URLS.get(site)
                        if url:
                            webbrowser.open(url)
                            message = f"Opening {site}"
                        else:
                            message = f"Don't know URL for {site}"
                    
                    self.speak(message, lang)
                    return True
        
        # =====================================================================
        # NEW: SEARCH COMMANDS
        # =====================================================================
        
        # Search on current platform (YouTube, Google, etc.)
        elif 'search for' in command_lower or 'find' in command_lower or 'look for' in command_lower:
            # Extract search query
            query = None
            if 'search for' in command_lower:
                query = command_lower.split('search for', 1)[1].strip()
            elif 'find' in command_lower:
                query = command_lower.split('find', 1)[1].strip()
            elif 'look for' in command_lower:
                query = command_lower.split('look for', 1)[1].strip()
            
            if query and self.workflow:
                success, message = self.workflow.handle_search_query(query)
                self.speak(message, lang)
            elif query:
                # Fallback to web search
                self.search_web(query)
            else:
                self.speak("What should I search for?", lang)
            
            return True
        
        # =====================================================================
        # NEW: WORKFLOW STATE HELP
        # =====================================================================
        
        # Contextual help
        elif 'help' in command_lower or 'what can' in command_lower:
            if self.workflow:
                help_msg = self.workflow.get_help_message()
                self.speak(help_msg, lang)
            else:
                # Original help message
                if lang == 'ur':
                    help_text = """مسٹر امان، میں آپ کی مدد کر سکتا ہوں: ایپلیکیشنز کھولنے، ویب تلاش کرنے،
                    وقت اور تاریخ بتانے، روشنی اور آواز کنٹرول کرنے، موسیقی چلانے،
                    وائی فائی اور بلوٹوتھ کنٹرول کرنے، بیٹری اور سسٹم کی معلومات لینے میں۔"""
                else:
                    help_text = """Hello Mr Amaan! I can help you with: opening apps, web search, time and date,
                    brightness and volume control, music playback, WiFi and Bluetooth,
                    battery info, system information, screenshots, and more!
                    
                    NEW: I can now help you with sequential workflows!
                    Try: 'Open Chrome' then 'Profile 1' then 'YouTube'"""
                self.speak(help_text, lang)
            return True
```

## Where to add this:

1. Open `voice_assistant_advanced.py`
2. Find the `process_command` method (around line 570)
3. After the greeting section (around line 600-610), add ALL the code above
4. Make sure indentation matches (should be at the same level as other `elif` statements)

## Result:

After adding this, you'll have:
- ✅ Workflow-aware profile selection
- ✅ "What apps are running?" command
- ✅ "How many Chrome windows?" command
- ✅ Smart Chrome opening with profiles
- ✅ Smart website opening
- ✅ "Search for X" on current platform
- ✅ Contextual help based on current state

## Testing:

After integration, try:
```
"What apps are running?"
"Open Chrome"
"Profile 1"
"YouTube"
"Search for Python tutorials"
```
