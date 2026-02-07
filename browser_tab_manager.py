"""
Browser Tab Manager - Detect and control open browser tabs
Supports Chrome, Chromium, Firefox
Enhanced with robust error handling and dependency checking
"""

import subprocess
import logging
from typing import List, Dict, Optional, Tuple

from constants import (
    WEBSITE_PATTERNS, SUBPROCESS_SHORT_TIMEOUT,
    ERROR_WMCTRL_MISSING, ERROR_NO_TABS
)
from error_handling import (
    safe_subprocess_run, DependencyMissingError
)

logger = logging.getLogger(__name__)

class BrowserTabManager:
    """Manage browser tabs - detect, switch, close"""
    
    def __init__(self):
        self.chrome_installed = self._check_browser('google-chrome')
        self.chromium_installed = self._check_browser('chromium-browser')
        self.firefox_installed = self._check_browser('firefox')
        
        # Check wmctrl availability
        self.wmctrl_available = self._check_wmctrl()
        
        if not self.wmctrl_available:
            logger.warning(
                "wmctrl is not installed. Tab management will be limited. "
                "Install it with: sudo apt install wmctrl"
            )
        
        # Website patterns from constants
        self.website_patterns = WEBSITE_PATTERNS
    
    def _check_browser(self, browser_command: str) -> bool:
        """Check if browser is installed"""
        try:
            success, _, _ = safe_subprocess_run(
                ['which', browser_command],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            return success
        except Exception as e:
            logger.debug(f"Browser check failed for {browser_command}: {e}")
            return False
    
    def _check_wmctrl(self) -> bool:
        """Check if wmctrl is installed"""
        try:
            success, _, _ = safe_subprocess_run(
                ['which', 'wmctrl'],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            return success
        except Exception:
            return False
    
    def _ensure_wmctrl(self) -> None:
        """Ensure wmctrl is available or raise error"""
        if not self.wmctrl_available:
            raise DependencyMissingError(ERROR_WMCTRL_MISSING)
    
    def get_chrome_tabs(self) -> List[Dict[str, str]]:
        """
        Get list of open Chrome/Chromium tabs
        Returns: list of {title, window_id, browser}
        """
        if not self.wmctrl_available:
            logger.debug("wmctrl not available, cannot get Chrome tabs")
            return []
        
        tabs = []
        
        try:
            success, stdout, stderr = safe_subprocess_run(
                ['wmctrl', '-l'],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            
            if not success:
                logger.debug(f"wmctrl failed: {stderr}")
                return []
            
            for line in stdout.split('\n'):
                if not line.strip():
                    continue
                
                if 'Google Chrome' in line or 'Chromium' in line:
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        window_id = parts[0]
                        title = parts[3]
                        
                        # Clean up title
                        title = title.replace(' - Google Chrome', '')
                        title = title.replace(' - Chromium', '')
                        
                        tabs.append({
                            'title': title.strip(),
                            'window_id': window_id,
                            'browser': 'chrome'
                        })
        
        except Exception as e:
            logger.debug(f"Error getting Chrome tabs: {e}")
        
        return tabs
    
    def get_firefox_tabs(self) -> List[Dict[str, str]]:
        """
        Get list of open Firefox tabs
        Returns: list of {title, window_id, browser}
        """
        if not self.wmctrl_available:
            logger.debug("wmctrl not available, cannot get Firefox tabs")
            return []
        
        tabs = []
        
        try:
            success, stdout, stderr = safe_subprocess_run(
                ['wmctrl', '-l'],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            
            if not success:
                logger.debug(f"wmctrl failed: {stderr}")
                return []
            
            for line in stdout.split('\n'):
                if not line.strip():
                    continue
                
                if 'Mozilla Firefox' in line or 'Firefox' in line:
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        window_id = parts[0]
                        title = parts[3]
                        
                        # Clean up title
                        title = title.replace(' - Mozilla Firefox', '')
                        title = title.replace(' — Mozilla Firefox', '')
                        
                        tabs.append({
                            'title': title.strip(),
                            'window_id': window_id,
                            'browser': 'firefox'
                        })
        
        except Exception as e:
            logger.debug(f"Error getting Firefox tabs: {e}")
        
        return tabs
    
    def get_all_tabs(self) -> List[Dict[str, str]]:
        """Get all open browser tabs from all browsers"""
        all_tabs = []
        
        if self.chrome_installed or self.chromium_installed:
            all_tabs.extend(self.get_chrome_tabs())
        
        if self.firefox_installed:
            all_tabs.extend(self.get_firefox_tabs())
        
        return all_tabs
    
    def find_tab_by_website(self, website_name: str) -> Optional[Dict[str, str]]:
        """
        Find tab by website name (e.g., 'youtube', 'gmail')
        Returns: tab dict or None
        """
        website_name = website_name.lower().strip()
        all_tabs = self.get_all_tabs()
        
        if not all_tabs:
            return None
        
        # Get patterns for this website
        patterns = self.website_patterns.get(website_name, [website_name])
        
        for tab in all_tabs:
            title_lower = tab['title'].lower()
            
            # Check if any pattern matches
            for pattern in patterns:
                if pattern in title_lower:
                    logger.debug(f"Found tab: {tab['title']} matches {website_name}")
                    return tab
        
        return None
    
    def switch_to_tab(self, tab: Dict[str, str]) -> Tuple[bool, str]:
        """
        Switch to a specific tab
        
        Args:
            tab: dict with 'window_id' and 'title' keys
            
        Returns:
            (success, message) tuple
        """
        try:
            self._ensure_wmctrl()
            
            if 'window_id' not in tab:
                return False, "Tab has no window_id"
            
            success, stdout, stderr = safe_subprocess_run(
                ['wmctrl', '-ia', tab['window_id']],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            
            if success:
                logger.info(f"Switched to tab: {tab['title']}")
                return True, f"Switched to {tab['title']}"
            else:
                logger.warning(f"Failed to switch to tab: {stderr}")
                return False, "Could not switch to tab"
        
        except DependencyMissingError as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Tab switch error: {e}")
            return False, f"Error: {str(e)}"
    
    def close_tab(self, tab: Dict[str, str]) -> Tuple[bool, str]:
        """
        Close a specific tab
        
        Args:
            tab: dict with 'window_id' and 'title' keys
            
        Returns:
            (success, message) tuple
        """
        try:
            self._ensure_wmctrl()
            
            if 'window_id' not in tab:
                return False, "Tab has no window_id"
            
            success, stdout, stderr = safe_subprocess_run(
                ['wmctrl', '-ic', tab['window_id']],
                timeout=SUBPROCESS_SHORT_TIMEOUT,
                check=False
            )
            
            if success:
                logger.info(f"Closed tab: {tab['title']}")
                return True, f"Closed {tab['title']}"
            else:
                logger.warning(f"Failed to close tab: {stderr}")
                return False, "Could not close tab"
        
        except DependencyMissingError as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Tab close error: {e}")
            return False, f"Error: {str(e)}"
    
    def is_website_open(self, website_name: str) -> bool:
        """Check if a specific website is already open"""
        tab = self.find_tab_by_website(website_name)
        return tab is not None
    
    def get_tab_count(self) -> int:
        """Get total number of open tabs"""
        return len(self.get_all_tabs())
    
    def get_summary(self) -> Dict:
        """Get summary of open tabs"""
        tabs = self.get_all_tabs()
        
        summary = {
            'total': len(tabs),
            'chrome': len([t for t in tabs if t.get('browser') == 'chrome']),
            'firefox': len([t for t in tabs if t.get('browser') == 'firefox']),
            'tabs': [t['title'] for t in tabs],
            'wmctrl_available': self.wmctrl_available
        }
        
        return summary


# Quick test function
if __name__ == "__main__":
    print("Testing Browser Tab Manager...")
    
    manager = BrowserTabManager()
    
    print(f"\nBrowsers detected:")
    print(f"Chrome: {manager.chrome_installed}")
    print(f"Chromium: {manager.chromium_installed}")
    print(f"Firefox: {manager.firefox_installed}")
    
    print("\n" + "="*60)
    print("Getting all open tabs...")
    tabs = manager.get_all_tabs()
    
    if tabs:
        print(f"\nFound {len(tabs)} tabs:")
        for i, tab in enumerate(tabs, 1):
            print(f"{i}. [{tab['browser']}] {tab['title']}")
    else:
        print("No tabs found (or no browser is open)")
    
    print("\n" + "="*60)
    print("Testing website detection...")
    
    test_sites = ['youtube', 'gmail', 'github']
    for site in test_sites:
        tab = manager.find_tab_by_website(site)
        if tab:
            print(f"✅ {site.capitalize()} is open: {tab['title']}")
        else:
            print(f"❌ {site.capitalize()} is not open")
    
    print("\n" + "="*60)
    summary = manager.get_summary()
    print(f"Summary:")
    print(f"Total tabs: {summary['total']}")
    print(f"Chrome tabs: {summary['chrome']}")
    print(f"Firefox tabs: {summary['firefox']}")
