"""
Desktop App Detector - Detect and list running applications
Uses wmctrl and ps to detect what's currently running on desktop
"""

import subprocess
import logging
from typing import List, Dict, Optional
import psutil

from error_handling import safe_subprocess_run

logger = logging.getLogger(__name__)

class DesktopAppDetector:
    """Detect and manage desktop applications"""
    
    def __init__(self):
        self.wmctrl_available = self._check_wmctrl()
        
        # Common app process names
        self.app_patterns = {
            'chrome': ['chrome', 'google-chrome'],
            'firefox': ['firefox'],
            'code': ['code', 'code-oss'],
            'terminal': ['gnome-terminal', 'konsole', 'xterm'],
            'files': ['nautilus', 'dolphin', 'thunar'],
            'calculator': ['gnome-calculator', 'kcalc'],
            'settings': ['gnome-control-center', 'systemsettings'],
            'music': ['rhythmbox', 'spotify'],
            'videos': ['totem', 'vlc'],
        }
    
    def _check_wmctrl(self) -> bool:
        """Check if wmctrl is available"""
        try:
            success, _, _ = safe_subprocess_run(['which', 'wmctrl'], check=False)
            return success
        except:
            return False
    
    def get_all_windows(self) -> List[Dict[str, str]]:
        """
        Get all open windows
        Returns: [{title, window_id, desktop, class}]
        """
        if not self.wmctrl_available:
            logger.warning("wmctrl not available")
            return []
        
        windows = []
        
        try:
            success, stdout, _ = safe_subprocess_run(['wmctrl', '-lx'], check=False)
            
            if not success:
                return []
            
            for line in stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    window = {
                        'window_id': parts[0],
                        'desktop': parts[1],
                        'class': parts[2],
                        'machine': parts[3],
                        'title': parts[4]
                    }
                    windows.append(window)
        
        except Exception as e:
            logger.error(f"Error getting windows: {e}")
        
        return windows
    
    def get_running_apps(self) -> List[Dict[str, any]]:
        """
        Get list of running applications
        Returns: [{name, process_name, pid, window_count}]
        """
        apps = {}
        
        # Get all processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                
                # Check if this is a known app
                for app_name, patterns in self.app_patterns.items():
                    if any(pattern in name for pattern in patterns):
                        if app_name not in apps:
                            apps[app_name] = {
                                'name': app_name,
                                'process_name': proc.info['name'],
                                'pids': [],
                                'window_count': 0
                            }
                        apps[app_name]['pids'].append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Get window counts from wmctrl
        if self.wmctrl_available:
            windows = self.get_all_windows()
            for window in windows:
                window_class = window['class'].lower()
                for app_name in apps:
                    if app_name in window_class:
                        apps[app_name]['window_count'] += 1
        
        return list(apps.values())
    
    def get_app_summary(self) -> str:
        """Get human-readable summary of running apps"""
        apps = self.get_running_apps()
        
        if not apps:
            return "No applications detected"
        
        summary_lines = [f"Found {len(apps)} running applications:"]
        
        for app in apps:
            instances = len(app['pids'])
            windows = app['window_count']
            
            if windows > 0:
                summary_lines.append(
                    f"  • {app['name'].title()}: {instances} process(es), {windows} window(s)"
                )
            else:
                summary_lines.append(
                    f"  • {app['name'].title()}: {instances} process(es)"
                )
        
        return '\n'.join(summary_lines)
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if a specific app is running"""
        app_name = app_name.lower()
        apps = self.get_running_apps()
        
        return any(app['name'] == app_name for app in apps)
    
    def count_app_instances(self, app_name: str) -> int:
        """Count how many instances of an app are running"""
        app_name = app_name.lower()
        apps = self.get_running_apps()
        
        for app in apps:
            if app['name'] == app_name:
                return len(app['pids'])
        
        return 0
    
    def get_window_list(self, app_name: str = None) -> List[str]:
        """
        Get list of window titles
        If app_name provided, filter by that app
        """
        windows = self.get_all_windows()
        
        if app_name:
            app_name = app_name.lower()
            windows = [w for w in windows if app_name in w['class'].lower()]
        
        return [w['title'] for w in windows]
    
    def focus_window(self, window_title_pattern: str) -> tuple[bool, str]:
        """
        Focus a window by title pattern
        """
        if not self.wmctrl_available:
            return False, "wmctrl not available"
        
        try:
            # Use wmctrl to activate window
            success, _, stderr = safe_subprocess_run(
                ['wmctrl', '-a', window_title_pattern],
                check=False
            )
            
            if success:
                return True, f"Focused window: {window_title_pattern}"
            else:
                return False, f"Window not found: {window_title_pattern}"
        
        except Exception as e:
            return False, f"Error focusing window: {e}"
