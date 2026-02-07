"""
Error Handling Utilities
Provides consistent error handling and safe operation wrappers
"""

import logging
import subprocess
from typing import Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class VoiceAssistantError(Exception):
    """Base exception for voice assistant errors"""
    pass

class DependencyMissingError(VoiceAssistantError):
    """Raised when required dependency is missing"""
    pass

# ============================================================================
# SAFE OPERATION WRAPPERS
# ============================================================================

def safe_subprocess_run(command: list, timeout: int = 5, 
                       check: bool = True) -> Tuple[bool, str, str]:
    """
    Safely run a subprocess command
    
    Args:
        command: Command list to execute
        timeout: Timeout in seconds
        check: Whether to check return code
        
    Returns:
        (success, stdout, stderr) tuple
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            check=check,
            text=True
        )
        return True, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out: {' '.join(command)}")
        return False, "", "Command timed out"
    except subprocess.CalledProcessError as e:
        logger.warning(f"Command failed: {' '.join(command)}")
        return False, e.stdout or "", e.stderr or ""
    except FileNotFoundError:
        logger.error(f"Command not found: {command[0]}")
        return False, "", f"Command not found: {command[0]}"
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        return False, "", str(e)

def safe_file_read(filepath: str, default: str = "") -> str:
    """
    Safely read a file
    
    Args:
        filepath: Path to file
        default: Default value if file cannot be read
        
    Returns:
        File contents or default value
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.debug(f"File not found: {filepath}")
        return default
    except PermissionError:
        logger.warning(f"Permission denied reading file: {filepath}")
        return default
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return default

def safe_file_write(filepath: str, content: str) -> bool:
    """
    Safely write to a file
    
    Args:
        filepath: Path to file
        content: Content to write
        
    Returns:
        True if successful
    """
    try:
        import os
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except PermissionError:
        logger.error(f"Permission denied writing file: {filepath}")
        return False
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False

# ============================================================================
# DEPENDENCY CHECKING
# ============================================================================

def check_command_exists(command: str) -> bool:
    """Check if a command exists in system PATH"""
    try:
        subprocess.run(['which', command], 
                      capture_output=True, 
                      check=True, 
                      timeout=2)
        return True
    except:
        return False

# ============================================================================
# INPUT SANITIZATION
# ============================================================================

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove dangerous characters
    dangerous_chars = ['`', '$', '|', ';', '&', '>', '<', '\n', '\r']
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    return sanitized[:max_length].strip()
