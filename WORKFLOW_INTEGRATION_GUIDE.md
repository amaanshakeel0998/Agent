# 🚀 Workflow & App Detection Integration Guide

## New Features Added

### 1. **Workflow Manager** (`workflow_manager.py`)
Enables sequential command execution:
```
You: "Open Chrome"
→ "Profile 1"  
→ "YouTube"
→ "Search Python"
```

### 2. **Desktop App Detector** (`desktop_app_detector.py`)
Detects all running apps and windows:
```
You: "What apps are running?"
Assistant: "Chrome (2 windows), Firefox (1 window), Terminal..."
```

---

## 📦 Installation Steps

### Step 1: Copy New Files
Make sure you have these new files:
- `workflow_manager.py`
- `desktop_app_detector.py`

### Step 2: Install Dependencies
```bash
# psutil is already in requirements
pip install psutil --break-system-packages

# Make sure wmctrl is installed
sudo apt install wmctrl
```

### Step 3: Update `voice_assistant_advanced.py`

Add these imports at the top (around line 28):
```python
from workflow_manager import WorkflowManager, WorkflowState
from desktop_app_detector import DesktopAppDetector
```

Add initialization in `__init__` method (around line 419):
```python
# Desktop App Detector - NEW!
self.app_detector = DesktopAppDetector()
self.logger.info("Desktop app detector initialized")

# Workflow Manager - NEW!
self.workflow = WorkflowManager(self.context, self.tab_manager)
self.logger.info("Workflow manager initialized")
```

### Step 4: Add New Commands

Add these command handlers in `process_command()` method:

#### A. Check What's Running
```python
# NEW: List running apps
elif 'what' in command_lower and ('app' in command_lower or 'running' in command_lower or 'open' in command_lower):
    summary = self.app_detector.get_app_summary()
    self.speak(summary, lang)
    return True
```

#### B. Smart Chrome Opening
Replace the existing Chrome opening code with:
```python
# Open Chrome with workflow support
elif 'chrome' in command_lower and ('open' in command_lower or 'کھولو' in command_lower):
    # Check if asking for specific profile
    profile = None
    if 'profile' in command_lower or 'amaan' in command_lower:
        if 'profile 1' in command_lower or 'amaan' in command_lower or '1' in command_lower:
            profile = 'profile 1'
        elif 'profile 2' in command_lower or 'work' in command_lower or '2' in command_lower:
            profile = 'profile 2'
    
    success, message = self.workflow.handle_browser_opening('chrome', profile)
    self.speak(message, lang)
    return True
```

#### C. Profile Selection (When Chrome is open)
```python
# NEW: Handle profile selection
elif self.workflow.state == WorkflowState.PROFILE_SELECTION:
    # User is selecting Chrome profile
    success, message = self.workflow.handle_profile_selection(command_lower)
    self.speak(message, lang)
    return True
```

#### D. Smart Website Opening
```python
# Open websites (enhanced with workflow)
elif any(site in command_lower for site in ['youtube', 'gmail', 'google', 'facebook', 'github']):
    for site in ['youtube', 'gmail', 'google', 'facebook', 'github', 'reddit']:
        if site in command_lower:
            success, message = self.workflow.handle_website_opening(site)
            self.speak(message, lang)
            return True
```

#### E. Search Commands
```python
# NEW: Search on current platform
elif 'search for' in command_lower or 'تلاش کرو' in command_lower:
    # Extract search query
    if 'search for' in command_lower:
        query = command_lower.split('search for', 1)[1].strip()
    elif 'تلاش کرو' in command_lower:
        query = command_lower.split('تلاش کرو', 1)[1].strip()
    else:
        query = command_lower
    
    if query:
        success, message = self.workflow.handle_search_query(query)
        self.speak(message, lang)
    else:
        self.speak("What should I search for?", lang)
    return True
```

#### F. Workflow Help
```python
# NEW: Contextual help
elif 'help' in command_lower or 'what can i do' in command_lower:
    help_msg = self.workflow.get_help_message()
    self.speak(help_msg, lang)
    return True
```

---

## 🎯 Example Workflows

### Workflow 1: Open Chrome with Profile
```
You: "Alexa, open Chrome"
Assistant: "Chrome is opening. Which profile? Say 'Profile 1' or 'Amaan'"

You: "Profile 1"
Assistant: "Opened Profile 1 profile. What would you like to do?"

You: "YouTube"
Assistant: "Opening YouTube"

You: "Search for Python tutorials"
Assistant: "Searching for Python tutorials"
```

### Workflow 2: Check Running Apps
```
You: "Alexa, what apps are running?"
Assistant: "Found 5 running applications:
  • Chrome: 1 process, 3 windows
  • Terminal: 2 processes, 2 windows
  • Files: 1 process, 1 window
  • Code: 1 process, 2 windows
  • Calculator: 1 process, 1 window"
```

### Workflow 3: Quick Chrome + Profile + Site
```
You: "Alexa, open Chrome with Profile 1"
Assistant: "Chrome opened with Profile 1"

You: "Gmail"
Assistant: "Opening Gmail"
```

---

## 🔧 Advanced Features to Add Later

### 1. Screen Automation (pyautogui)
For clicking on profiles visually:
```bash
pip install pyautogui --break-system-packages
```

Then add to `workflow_manager.py`:
```python
import pyautogui

def click_profile_visually(self, profile_name):
    """Click on profile icon visually"""
    # Take screenshot
    # Find profile icon
    # Click it
    pass
```

### 2. Browser Automation (selenium)
For advanced control:
```bash
pip install selenium --break-system-packages
```

### 3. Window Switching
Already supported! Add command:
```python
elif 'switch to' in command_lower:
    app_name = command_lower.replace('switch to', '').strip()
    success, msg = self.app_detector.focus_window(app_name)
    self.speak(msg, lang)
```

---

## 📝 Testing

### Test 1: App Detection
```bash
# Open some apps manually
google-chrome &
gnome-terminal &
nautilus &

# Then ask assistant
"What apps are running?"
```

### Test 2: Chrome Workflow
```bash
"Open Chrome"
# Wait for it to open
"Profile 1"
# Wait for profile to open
"YouTube"
```

### Test 3: Search
```bash
"Open Chrome with Profile 1"
"YouTube"
"Search for coding tutorials"
```

---

## 🐛 Troubleshooting

### wmctrl not working?
```bash
sudo apt install wmctrl
```

### Profile selection not working?
The profile directories are hardcoded. Check your Chrome profiles:
```bash
ls ~/.config/google-chrome/
```

You'll see: `Default`, `Profile 1`, `Profile 2`, etc.

Update the mapping in `workflow_manager.py` if needed.

### Commands not being recognized in workflow?
Make sure you're updating `process_command()` to check workflow state:
```python
# Add this near the start of process_command()
if self.workflow.state != WorkflowState.IDLE:
    # We're in a workflow, handle it specially
    if self.workflow.state == WorkflowState.PROFILE_SELECTION:
        return self.workflow.handle_profile_selection(command_lower)
```

---

## 🎉 You're Ready!

After integration, you'll have:
- ✅ Sequential command execution
- ✅ Chrome profile selection
- ✅ Smart website opening
- ✅ Search on platforms
- ✅ See all running apps
- ✅ Context-aware help

**Next level:** Add pyautogui for visual clicking on profile icons!
