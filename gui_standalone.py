#!/usr/bin/env python3
"""
Voice Assistant with Rock-Solid GUI
Uses multiprocessing instead of threading to avoid segmentation faults
"""

import os
import sys
import tkinter as tk
import math
import time
from datetime import datetime
import socket

# Minimal imports for GUI process
print("🎨 Starting GUI...")

class VoiceAssistantGUI:
    """Standalone GUI that communicates via file"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant - وائس اسسٹنٹ")
        self.root.geometry("850x650")
        self.root.configure(bg='#0a0a0a')
        
        # State file for communication
        self.state_file = '/tmp/voice_assistant_state.txt'
        self.running = True
        
        # Colors
        self.bg = '#0a0a0a'
        self.green = '#00ff88'
        self.blue = '#0088ff'
        self.pink = '#ff0088'
        self.orange = '#ffaa00'
        
        # Animation state
        self.current_state = 'idle'
        self.wave_offset = 0
        self.glow_intensity = 0.2
        self.pulse_phase = 0
        
        self.setup_ui()
        self.start_animation()
        self.start_state_monitor()
        
        print("✅ GUI ready!")
    
    def setup_ui(self):
        """Setup UI"""
        # Title
        tk.Label(
            self.root,
            text="AI VOICE ASSISTANT",
            font=('Arial', 26, 'bold'),
            bg=self.bg,
            fg=self.green
        ).pack(pady=10)
        
        tk.Label(
            self.root,
            text="وائس اسسٹنٹ | English + Urdu",
            font=('Arial', 12),
            bg=self.bg,
            fg='#888888'
        ).pack(pady=(0, 10))
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="💤 Starting...",
            font=('Arial', 15, 'bold'),
            bg=self.bg,
            fg='#888888'
        )
        self.status_label.pack(pady=8)
        
        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=380,
            height=380,
            bg=self.bg,
            highlightthickness=0
        )
        self.canvas.pack(pady=15)
        
        # Transcript
        tk.Label(
            self.root,
            text="📝 Conversation:",
            font=('Arial', 11, 'bold'),
            bg=self.bg,
            fg='#888888',
            anchor='w'
        ).pack(fill=tk.X, padx=20)
        
        self.transcript = tk.Text(
            self.root,
            height=7,
            bg='#1a1a1a',
            fg='#ffffff',
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.transcript.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def draw_visualizer(self):
        """Draw animated visualizer"""
        self.canvas.delete('all')
        
        cx, cy = 190, 190
        base_radius = 75
        
        # State-based visuals
        if self.current_state == 'speaking':
            color = self.pink
            target_glow = 1.0
            wave_amp = 40
            icon = "🗣️"
        elif self.current_state == 'listening':
            color = self.blue
            target_glow = 0.7
            wave_amp = 25
            icon = "🎤"
        elif self.current_state == 'processing':
            color = self.orange
            target_glow = 0.5
            wave_amp = 15
            icon = "⚙️"
        else:  # idle
            color = '#888888'
            target_glow = 0.2
            wave_amp = 6
            icon = "💤"
        
        # Smooth glow
        self.glow_intensity += (target_glow - self.glow_intensity) * 0.08
        
        # Glow rings
        for i in range(5):
            r = base_radius + 55 - i * 11
            alpha = int(self.glow_intensity * (45 - i * 9))
            c = self.blend_color(color, alpha)
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=c, width=2)
        
        # Waveform
        points = []
        for i in range(61):
            angle = (i / 60) * 2 * math.pi
            wave = math.sin(angle * 4 + self.wave_offset) * wave_amp
            wave += math.sin(angle * 2 - self.wave_offset * 0.5) * wave_amp * 0.4
            pulse = math.sin(self.pulse_phase) * 10 * self.glow_intensity
            
            r = base_radius + wave + pulse
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))
        
        if points:
            self.canvas.create_line(points, fill=color, width=3, smooth=True)
        
        # Center
        self.canvas.create_oval(cx-28, cy-28, cx+28, cy+28, fill=self.bg, outline=color, width=2)
        self.canvas.create_text(cx, cy, text=icon, font=('Arial', 24))
        
        self.wave_offset += 0.09
        self.pulse_phase += 0.04
    
    def blend_color(self, hex_color, alpha):
        """Blend color"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            bg = 10
            r = int(bg + (r - bg) * (alpha / 255))
            g = int(bg + (g - bg) * (alpha / 255))
            b = int(bg + (b - bg) * (alpha / 255))
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return '#888888'
    
    def start_animation(self):
        """Animate at 30fps"""
        def animate():
            if self.running:
                try:
                    self.draw_visualizer()
                except:
                    pass
                self.root.after(33, animate)
        animate()
    
    def start_state_monitor(self):
        """Monitor state file"""
        def check_state():
            if self.running:
                try:
                    if os.path.exists(self.state_file):
                        with open(self.state_file, 'r') as f:
                            data = f.read().strip()
                            if data:
                                parts = data.split('|')
                                cmd = parts[0]
                                
                                if cmd == 'STATE':
                                    self.current_state = parts[1]
                                elif cmd == 'STATUS':
                                    self.status_label.config(text=parts[1], fg=parts[2] if len(parts) > 2 else '#888888')
                                elif cmd == 'MSG':
                                    msg_type = parts[1]
                                    text = parts[2]
                                    timestamp = datetime.now().strftime("%H:%M:%S")
                                    
                                    if msg_type == 'user':
                                        self.transcript.insert(tk.END, f"[{timestamp}] 👤 You: {text}\n")
                                        self.transcript.tag_add('user', "end-2l", "end-1l")
                                        self.transcript.tag_config('user', foreground=self.green)
                                    elif msg_type == 'assistant':
                                        self.transcript.insert(tk.END, f"[{timestamp}] 🤖 Assistant: {text}\n")
                                        self.transcript.tag_add('asst', "end-2l", "end-1l")
                                        self.transcript.tag_config('asst', foreground=self.blue)
                                    elif msg_type == 'system':
                                        self.transcript.insert(tk.END, f"[{timestamp}] ℹ️  {text}\n")
                                        self.transcript.tag_add('sys', "end-2l", "end-1l")
                                        self.transcript.tag_config('sys', foreground='#888888')
                                    
                                    self.transcript.see(tk.END)
                                elif cmd == 'EXIT':
                                    self.running = False
                                    self.root.quit()
                                    return
                except:
                    pass
                
                self.root.after(100, check_state)
        
        # Initialize state file
        try:
            with open(self.state_file, 'w') as f:
                f.write('STATE|idle')
        except:
            pass
        
        check_state()
    
    def run(self):
        """Run GUI"""
        def on_close():
            self.running = False
            try:
                with open(self.state_file, 'w') as f:
                    f.write('EXIT|gui')
            except:
                pass
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

if __name__ == "__main__":
    gui = VoiceAssistantGUI()
    gui.run()
