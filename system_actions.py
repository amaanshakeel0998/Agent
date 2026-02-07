"""
System Actions - Control system features like brightness, WiFi, power, etc.
"""

import subprocess
import os
import logging

logger = logging.getLogger(__name__)

class SystemActions:
    def __init__(self, config):
        self.config = config
    
    def _run_command(self, command, shell=False):
        """Run a system command safely"""
        try:
            result = subprocess.run(
                command if not shell else command,
                shell=shell,
                capture_output=True,
                timeout=5,
                check=True
            )
            return True, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return False, str(e)
    
    def control_brightness(self, action):
        """Control screen brightness"""
        try:
            if 'increase' in action or 'up' in action or 'بڑھا' in action:
                subprocess.run(['xdotool', 'key', 'XF86MonBrightnessUp'], check=True)
                return True, "Brightness increased"
            elif 'decrease' in action or 'down' in action or 'کم' in action:
                subprocess.run(['xdotool', 'key', 'XF86MonBrightnessDown'], check=True)
                return True, "Brightness decreased"
            elif 'maximum' in action or 'max' in action or 'پوری' in action:
                # Set to 100%
                subprocess.run(['brightnessctl', 'set', '100%'], check=True)
                return True, "Brightness set to maximum"
            elif 'minimum' in action or 'min' in action:
                # Set to 10%
                subprocess.run(['brightnessctl', 'set', '10%'], check=True)
                return True, "Brightness set to minimum"
            else:
                # Try to extract percentage
                import re
                match = re.search(r'(\d+)%?', action)
                if match:
                    percentage = match.group(1)
                    subprocess.run(['brightnessctl', 'set', f'{percentage}%'], check=True)
                    return True, f"Brightness set to {percentage}%"
            
            return False, "Unknown brightness command"
        except Exception as e:
            logger.error(f"Brightness control error: {e}")
            return False, str(e)
    
    def control_wifi(self, action):
        """Control WiFi connection"""
        try:
            if 'on' in action or 'enable' in action or 'چالو' in action:
                subprocess.run(['nmcli', 'radio', 'wifi', 'on'], check=True)
                return True, "WiFi enabled"
            elif 'off' in action or 'disable' in action or 'بند' in action:
                subprocess.run(['nmcli', 'radio', 'wifi', 'off'], check=True)
                return True, "WiFi disabled"
            elif 'status' in action or 'حالت' in action:
                result = subprocess.check_output(['nmcli', 'radio', 'wifi']).decode().strip()
                return True, f"WiFi is {result}"
            else:
                return False, "Unknown WiFi command"
        except Exception as e:
            logger.error(f"WiFi control error: {e}")
            return False, str(e)
    
    def control_bluetooth(self, action):
        """Control Bluetooth"""
        try:
            if 'on' in action or 'enable' in action or 'چالو' in action:
                subprocess.run(['bluetoothctl', 'power', 'on'], check=True)
                return True, "Bluetooth enabled"
            elif 'off' in action or 'disable' in action or 'بند' in action:
                subprocess.run(['bluetoothctl', 'power', 'off'], check=True)
                return True, "Bluetooth disabled"
            else:
                return False, "Unknown Bluetooth command"
        except Exception as e:
            logger.error(f"Bluetooth control error: {e}")
            return False, str(e)
    
    def power_action(self, action, confirm=True):
        """Shutdown, restart, or logout"""
        if confirm:
            response = input(f"⚠️  Are you sure you want to {action}? (yes/no): ")
            if response.lower() not in ['yes', 'y', 'ہاں']:
                return False, "Action cancelled"
        
        try:
            if 'shutdown' in action or 'بند کرو' in action:
                subprocess.Popen(['shutdown', '-h', 'now'])
                return True, "Shutting down..."
            elif 'restart' in action or 'reboot' in action or 'دوبارہ شروع' in action:
                subprocess.Popen(['reboot'])
                return True, "Restarting..."
            elif 'logout' in action or 'log out' in action:
                subprocess.Popen(['gnome-session-quit', '--logout', '--no-prompt'])
                return True, "Logging out..."
            elif 'sleep' in action or 'suspend' in action:
                subprocess.Popen(['systemctl', 'suspend'])
                return True, "Going to sleep..."
            else:
                return False, "Unknown power command"
        except Exception as e:
            logger.error(f"Power action error: {e}")
            return False, str(e)
    
    def lock_screen(self):
        """Lock the screen"""
        try:
            subprocess.Popen(['gnome-screensaver-command', '--lock'])
            return True, "Screen locked"
        except Exception as e:
            logger.error(f"Lock screen error: {e}")
            return False, str(e)
    
    def empty_trash(self, confirm=True):
        """Empty trash/recycle bin"""
        if confirm:
            response = input("⚠️  Empty trash? (yes/no): ")
            if response.lower() not in ['yes', 'y', 'ہاں']:
                return False, "Action cancelled"
        
        try:
            trash_path = os.path.expanduser('~/.local/share/Trash/files')
            if os.path.exists(trash_path):
                subprocess.run(['rm', '-rf', trash_path + '/*'], shell=True)
                return True, "Trash emptied"
            return False, "Trash folder not found"
        except Exception as e:
            logger.error(f"Empty trash error: {e}")
            return False, str(e)
    
    def get_battery_info(self):
        """Get battery information"""
        try:
            result = subprocess.check_output(
                ['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'],
                timeout=2
            ).decode()
            
            percentage = None
            state = None
            time_to_empty = None
            
            for line in result.split('\n'):
                if 'percentage:' in line:
                    percentage = line.split(':')[1].strip()
                if 'state:' in line:
                    state = line.split(':')[1].strip()
                if 'time to empty:' in line:
                    time_to_empty = line.split(':')[1].strip()
            
            info = f"Battery at {percentage}"
            if state:
                info += f", {state}"
            if time_to_empty:
                info += f", {time_to_empty} remaining"
            
            return True, info
        except Exception as e:
            logger.error(f"Battery info error: {e}")
            return False, "Could not get battery information"
    
    def get_disk_space(self):
        """Get disk space information"""
        try:
            result = subprocess.check_output(
                ['df', '-h', os.path.expanduser('~')],
                timeout=2
            ).decode()
            
            lines = result.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                info = f"Disk: {parts[2]} used of {parts[1]}, {parts[3]} available ({parts[4]} used)"
                return True, info
            return False, "Could not get disk information"
        except Exception as e:
            logger.error(f"Disk space error: {e}")
            return False, "Could not get disk space"
    
    def get_memory_info(self):
        """Get memory (RAM) information"""
        try:
            result = subprocess.check_output(['free', '-h'], timeout=2).decode()
            lines = result.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                total = parts[1]
                used = parts[2]
                available = parts[6]
                info = f"Memory: {used} used of {total}, {available} available"
                return True, info
            return False, "Could not get memory information"
        except Exception as e:
            logger.error(f"Memory info error: {e}")
            return False, "Could not get memory information"
