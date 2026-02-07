"""
Workflow Manager - Handle multi-step sequential tasks
Enables contextual command chains like:
  "Open Chrome" → "Profile 1" → "YouTube" → "Search X"
"""

import logging
import time
import subprocess
from enum import Enum
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    """Current state of workflow"""
    IDLE = "idle"
    BROWSER_STARTING = "browser_starting"
    PROFILE_SELECTION = "profile_selection"
    BROWSER_READY = "browser_ready"
    SEARCHING = "searching"
    VIDEO_PLAYING = "video_playing"
    APP_OPENING = "app_opening"

class Workflow:
    """Represents a multi-step workflow"""
    
    def __init__(self, name: str, steps: List[str]):
        self.name = name
        self.steps = steps
        self.current_step = 0
        self.data = {}  # Store workflow data
        self.created_at = time.time()
    
    def next_step(self) -> Optional[str]:
        """Get next step in workflow"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return self.current_step >= len(self.steps)
    
    def get_progress(self) -> str:
        """Get workflow progress"""
        return f"{self.current_step}/{len(self.steps)}"

class WorkflowManager:
    """Manages multi-step workflows and contextual commands"""
    
    def __init__(self, context_manager, tab_manager):
        self.context = context_manager
        self.tab_manager = tab_manager
        
        # Current state
        self.state = WorkflowState.IDLE
        self.current_workflow: Optional[Workflow] = None
        
        # State data
        self.waiting_for = None  # What we're waiting for user to say
        self.browser_process = None
        self.selected_profile = None
        self.current_url = None
        
        # Timeout for state transitions
        self.state_timeout = 10  # seconds
        self.state_started_at = None
        
        logger.info("Workflow Manager initialized")
    
    def start_workflow(self, workflow_name: str, steps: List[str]) -> None:
        """Start a new workflow"""
        self.current_workflow = Workflow(workflow_name, steps)
        logger.info(f"Started workflow: {workflow_name}")
    
    def cancel_workflow(self) -> None:
        """Cancel current workflow"""
        if self.current_workflow:
            logger.info(f"Cancelled workflow: {self.current_workflow.name}")
        self.current_workflow = None
        self.state = WorkflowState.IDLE
        self.waiting_for = None
    
    def set_state(self, new_state: WorkflowState, waiting_for: str = None):
        """Change workflow state"""
        logger.info(f"State: {self.state.value} → {new_state.value}")
        self.state = new_state
        self.waiting_for = waiting_for
        self.state_started_at = time.time()
    
    def is_state_expired(self) -> bool:
        """Check if current state has expired"""
        if self.state_started_at:
            return (time.time() - self.state_started_at) > self.state_timeout
        return False
    
    def get_current_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            'state': self.state.value,
            'waiting_for': self.waiting_for,
            'workflow': self.current_workflow.name if self.current_workflow else None,
            'workflow_progress': self.current_workflow.get_progress() if self.current_workflow else None
        }
    
    def handle_browser_opening(self, browser_name: str, profile: str = None) -> tuple[bool, str]:
        """
        Handle browser opening with profile selection
        
        Returns: (success, message)
        """
        # Set state to opening browser
        self.set_state(
            WorkflowState.BROWSER_STARTING,
            waiting_for="profile selection"
        )
        
        # Store info
        self.context.set_task(f"opening_{browser_name}")
        
        if browser_name.lower() == 'chrome':
            if profile:
                # Open with specific profile
                profile_dir = self._get_chrome_profile(profile)
                cmd = f'google-chrome --profile-directory="{profile_dir}"'
            else:
                # Open normally, will show profile selector
                cmd = 'google-chrome'
            
            try:
                self.browser_process = subprocess.Popen(cmd, shell=True)
                
                # Give browser time to start
                time.sleep(2)
                
                if profile:
                    # Profile specified, go directly to ready state
                    self.selected_profile = profile
                    self.set_state(WorkflowState.BROWSER_READY)
                    return True, f"Chrome opened with {profile} profile"
                else:
                    # Waiting for profile selection
                    self.set_state(
                        WorkflowState.PROFILE_SELECTION,
                        waiting_for="profile name (e.g., 'profile 1', 'amaan')"
                    )
                    return True, "Chrome is opening. Which profile? Say 'Profile 1' or 'Amaan'"
            
            except Exception as e:
                logger.error(f"Failed to open Chrome: {e}")
                self.set_state(WorkflowState.IDLE)
                return False, f"Failed to open Chrome: {e}"
        
        else:
            # Other browsers (Firefox, etc.)
            cmd = browser_name.lower()
            try:
                subprocess.Popen([cmd])
                time.sleep(2)
                self.set_state(WorkflowState.BROWSER_READY)
                return True, f"{browser_name} opened"
            except:
                self.set_state(WorkflowState.IDLE)
                return False, f"Failed to open {browser_name}"
    
    def handle_profile_selection(self, profile_input: str) -> tuple[bool, str]:
        """
        Handle Chrome profile selection
        Expects state to be PROFILE_SELECTION
        """
        if self.state != WorkflowState.PROFILE_SELECTION:
            return False, "Not in profile selection mode"
        
        # Parse profile from input
        profile_input = profile_input.lower().strip()
        
        # Map common names to profile directories
        profile_map = {
            'default': 'Default',
            'me': 'Default',
            'profile 1': 'Profile 1',
            'profile1': 'Profile 1',
            '1': 'Profile 1',
            'amaan': 'Profile 1',
            'profile 2': 'Profile 2',
            'profile2': 'Profile 2',
            '2': 'Profile 2',
            'work': 'Profile 2',
        }
        
        profile_dir = profile_map.get(profile_input)
        
        if not profile_dir:
            return False, f"Unknown profile: {profile_input}. Try 'Profile 1', 'Amaan', or 'Profile 2'"
        
        # Close current Chrome instance
        if self.browser_process:
            try:
                self.browser_process.terminate()
                time.sleep(0.5)
            except:
                pass
        
        # Open with selected profile using pyautogui to click
        # First, let's try command line
        cmd = f'google-chrome --profile-directory="{profile_dir}"'
        
        try:
            self.browser_process = subprocess.Popen(cmd, shell=True)
            self.selected_profile = profile_input
            time.sleep(2)
            
            self.set_state(WorkflowState.BROWSER_READY)
            
            return True, f"Opened {profile_input} profile. What would you like to do?"
        
        except Exception as e:
            logger.error(f"Profile selection failed: {e}")
            self.set_state(WorkflowState.IDLE)
            return False, f"Failed to open profile: {e}"
    
    def _get_chrome_profile(self, profile_name: str) -> str:
        """Get Chrome profile directory name"""
        profile_map = {
            'default': 'Default',
            'me': 'Default',
            'profile 1': 'Profile 1',
            'profile1': 'Profile 1',
            '1': 'Profile 1',
            'amaan': 'Profile 1',
            'profile 2': 'Profile 2',
            'profile2': 'Profile 2',
            '2': 'Profile 2',
            'work': 'Profile 2',
        }
        return profile_map.get(profile_name.lower(), 'Default')
    
    def handle_website_opening(self, website_name: str) -> tuple[bool, str]:
        """
        Open website in current browser
        Browser should be in READY state
        """
        if self.state not in [WorkflowState.BROWSER_READY, WorkflowState.IDLE]:
            # Browser not ready, check if any browser is open
            if not self.tab_manager or not self.tab_manager.get_all_tabs():
                return False, "No browser is open. Say 'Open Chrome' first"
        
        # Get URL for website
        from constants import WEBSITE_URLS
        
        url = WEBSITE_URLS.get(website_name.lower())
        
        if not url:
            # Try generic search
            url = f"https://www.google.com/search?q={website_name}"
        
        # Open URL
        import webbrowser
        webbrowser.open(url)
        
        self.current_url = url
        
        return True, f"Opening {website_name}"
    
    def handle_search_query(self, query: str, platform: str = None) -> tuple[bool, str]:
        """
        Handle search on current platform (YouTube, Google, etc.)
        """
        # Detect platform from current state or tabs
        if not platform:
            # Try to detect from open tabs
            if self.tab_manager:
                tabs = self.tab_manager.get_all_tabs()
                for tab in tabs:
                    if 'youtube' in tab['title'].lower():
                        platform = 'youtube'
                        break
                    elif 'google' in tab['title'].lower():
                        platform = 'google'
                        break
        
        if platform == 'youtube':
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            # Default to Google
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        import webbrowser
        webbrowser.open(url)
        
        return True, f"Searching for {query}"
    
    def get_help_message(self) -> str:
        """Get contextual help based on current state"""
        if self.state == WorkflowState.IDLE:
            return "Ready! Try: 'Open Chrome', 'Open Firefox', or 'What apps are running?'"
        
        elif self.state == WorkflowState.PROFILE_SELECTION:
            return "Chrome is open. Say: 'Profile 1', 'Amaan', 'Profile 2', or 'Default'"
        
        elif self.state == WorkflowState.BROWSER_READY:
            return "Browser ready! Say: 'YouTube', 'Gmail', 'Search for X'"
        
        elif self.state == WorkflowState.SEARCHING:
            return "On search page. Say: 'Play first video', 'Next page'"
        
        return f"Current state: {self.state.value}"
