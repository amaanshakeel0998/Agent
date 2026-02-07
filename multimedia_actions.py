"""
Multimedia Actions - Control music, videos, and media playback
"""

import subprocess
import os
import glob
import logging

logger = logging.getLogger(__name__)

class MultimediaActions:
    def __init__(self, config):
        self.config = config
        self.music_player = config.get('System', 'music_player', fallback='rhythmbox')
        self.video_player = config.get('System', 'video_player', fallback='totem')
        self.current_player = None
    
    def _control_media(self, action):
        """Control media playback using playerctl"""
        try:
            if action in ['play', 'pause', 'play-pause', 'next', 'previous', 'stop']:
                subprocess.run(['playerctl', action], check=True, timeout=2)
                return True
            return False
        except Exception as e:
            logger.error(f"Media control error: {e}")
            return False
    
    def play_pause(self):
        """Toggle play/pause"""
        if self._control_media('play-pause'):
            return True, "Toggled playback"
        return False, "No media player found"
    
    def play(self):
        """Play media"""
        if self._control_media('play'):
            return True, "Playing"
        return False, "No media player found"
    
    def pause(self):
        """Pause media"""
        if self._control_media('pause'):
            return True, "Paused"
        return False, "No media player found"
    
    def stop(self):
        """Stop media"""
        if self._control_media('stop'):
            return True, "Stopped"
        return False, "No media player found"
    
    def next_track(self):
        """Next track/video"""
        if self._control_media('next'):
            return True, "Next track"
        return False, "No media player found"
    
    def previous_track(self):
        """Previous track/video"""
        if self._control_media('previous'):
            return True, "Previous track"
        return False, "No media player found"
    
    def get_current_track(self):
        """Get currently playing track information"""
        try:
            title = subprocess.check_output(
                ['playerctl', 'metadata', 'title'],
                timeout=2
            ).decode().strip()
            
            artist = subprocess.check_output(
                ['playerctl', 'metadata', 'artist'],
                timeout=2
            ).decode().strip()
            
            if title and artist:
                return True, f"Now playing: {title} by {artist}"
            elif title:
                return True, f"Now playing: {title}"
            else:
                return False, "No track information available"
        except Exception as e:
            logger.error(f"Get track info error: {e}")
            return False, "No media playing"
    
    def open_music_player(self):
        """Open music player"""
        try:
            subprocess.Popen([self.music_player])
            return True, f"Opening {self.music_player}"
        except Exception as e:
            logger.error(f"Open music player error: {e}")
            return False, f"Could not open {self.music_player}"
    
    def play_music_from_directory(self, query=None):
        """Play music from Music directory"""
        try:
            music_dir = os.path.expanduser('~/Music')
            
            if not os.path.exists(music_dir):
                return False, "Music directory not found"
            
            # Find music files
            music_files = []
            for ext in ['*.mp3', '*.flac', '*.wav', '*.ogg', '*.m4a']:
                music_files.extend(glob.glob(os.path.join(music_dir, '**', ext), recursive=True))
            
            if not music_files:
                return False, "No music files found"
            
            # If query provided, try to find matching file
            if query:
                query_lower = query.lower()
                matching_files = [f for f in music_files if query_lower in os.path.basename(f).lower()]
                if matching_files:
                    music_files = matching_files
            
            # Play first file or random
            import random
            file_to_play = random.choice(music_files) if not query else music_files[0]
            
            subprocess.Popen([self.music_player, file_to_play])
            filename = os.path.basename(file_to_play)
            return True, f"Playing {filename}"
        
        except Exception as e:
            logger.error(f"Play music error: {e}")
            return False, "Could not play music"
    
    def open_video_player(self, video_file=None):
        """Open video player"""
        try:
            if video_file:
                subprocess.Popen([self.video_player, video_file])
                return True, f"Opening video: {os.path.basename(video_file)}"
            else:
                subprocess.Popen([self.video_player])
                return True, f"Opening {self.video_player}"
        except Exception as e:
            logger.error(f"Open video player error: {e}")
            return False, f"Could not open {self.video_player}"
    
    def control_volume_percentage(self, percentage):
        """Set volume to specific percentage"""
        try:
            subprocess.run(['amixer', 'set', 'Master', f'{percentage}%'], check=True)
            return True, f"Volume set to {percentage}%"
        except Exception as e:
            logger.error(f"Volume control error: {e}")
            return False, "Could not control volume"
    
    def get_volume(self):
        """Get current volume level"""
        try:
            result = subprocess.check_output(
                ['amixer', 'get', 'Master'],
                timeout=2
            ).decode()
            
            # Parse volume percentage
            import re
            match = re.search(r'\[(\d+)%\]', result)
            if match:
                volume = match.group(1)
                return True, f"Volume is at {volume}%"
            return False, "Could not get volume"
        except Exception as e:
            logger.error(f"Get volume error: {e}")
            return False, "Could not get volume"
    
    def take_screenshot(self, delay=0):
        """Take a screenshot"""
        try:
            timestamp = subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()
            screenshot_path = os.path.expanduser(f"~/Pictures/screenshot_{timestamp}.png")
            
            if delay > 0:
                subprocess.run(['gnome-screenshot', '-d', str(delay), '-f', screenshot_path], check=True)
                return True, f"Screenshot saved (after {delay}s delay)"
            else:
                subprocess.run(['gnome-screenshot', '-f', screenshot_path], check=True)
                return True, "Screenshot saved"
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False, "Could not take screenshot"
    
    def record_screen(self, duration=10):
        """Record screen video (requires simplescreenrecorder or similar)"""
        try:
            # This is a placeholder - actual implementation depends on available tools
            return False, "Screen recording not yet implemented"
        except Exception as e:
            logger.error(f"Screen recording error: {e}")
            return False, "Could not record screen"
