import customtkinter as ctk
import sounddevice as sd
import whisper  # Using openai-whisper instead of faster-whisper
import threading
import numpy as np
import wave
import os
import torch
import time
# import language_tool_python  # DISABLED - Grammar correction temporarily disabled
import pyautogui
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key
from collections import deque
import random
import re

class SimpleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FastSTT (OpenAI Whisper)")
        self.geometry("200x300")
        self.attributes('-topmost', True)
        
        # Make window draggable
        self.bind('<Button-1>', self.click_window)
        self.bind('<B1-Motion>', self.drag_window)
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Position window in bottom right corner
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 250
        y = screen_height - 350
        self.geometry(f"+{x}+{y}")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Waveform canvas
        self.canvas = ctk.CTkCanvas(
            self.main_frame,
            width=180,
            height=150,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(pady=(0, 10))
        
        # Record button
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text="🎤 Record",
            command=self.toggle_recording,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            corner_radius=20
        )
        self.record_button.pack(pady=(0, 10))
        
        # Waveform parameters
        self.num_bars = 15
        self.bar_width = 8
        self.bar_spacing = 4
        self.canvas_width = 180
        self.canvas_height = 150
        self.waveform_bars = []
        self.audio_levels = deque(maxlen=self.num_bars)
        
        # Initialize waveform
        self.init_waveform()
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.samplerate = 44100
        self.channels = 1
        self.temp_wav_file = "temp_audio.wav"
        
        # Audio monitoring
        self.audio_level = 0
        self.last_levels = deque(maxlen=5)
        
        # Fixed settings
        self.model_name = "large-v3-turbo"
        self.auto_insert = True
        self.grammar_correction = False  # DISABLED - Grammar correction temporarily disabled
        self.immediate_insert = True

        # Initialize grammar tool
        self.grammar_tool = None  # DISABLED - Not using grammar correction
        
        # Global hotkey
        self.hotkey = Key.f8
        self.setup_global_hotkey()
        
        # Load model
        self.model = None
        threading.Thread(target=self.load_model, daemon=True).start()
        
    def init_waveform(self):
        """Initialize waveform bars"""
        self.waveform_bars = []
        self.audio_levels.clear()
        
        # Calculate starting position
        total_width = self.num_bars * self.bar_width + (self.num_bars - 1) * self.bar_spacing
        start_x = (self.canvas_width - total_width) // 2
        
        for i in range(self.num_bars):
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            # Create bar (initially flat)
            bar = self.canvas.create_rectangle(
                x, self.canvas_height // 2 - 2,
                x + self.bar_width, self.canvas_height // 2 + 2,
                fill="#3B8ED0",
                outline=""
            )
            self.waveform_bars.append(bar)
            self.audio_levels.append(0)
    
    def update_waveform(self, audio_level):
        """Update waveform bars based on audio level"""
        if not self.is_recording:
            return
            
        # Normalize audio level
        normalized_level = min(audio_level / 3000, 1.0)
        
        # Add some smoothing
        self.last_levels.append(normalized_level)
        smooth_level = sum(self.last_levels) / len(self.last_levels)
        
        # Shift existing levels and add new one
        self.audio_levels.append(smooth_level)
        
        # Update bars
        for i, (bar, level) in enumerate(zip(self.waveform_bars, self.audio_levels)):
            # Add some randomness for natural look
            random_factor = 0.7 + random.random() * 0.6
            display_level = level * random_factor
            
            # Calculate bar height (minimum 4 pixels, max 120 pixels)
            bar_height = max(4, int(display_level * 120))
            
            # Calculate bar position
            start_x = (self.canvas_width - (self.num_bars * (self.bar_width + self.bar_spacing) - self.bar_spacing)) // 2
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            y1 = (self.canvas_height - bar_height) // 2
            y2 = y1 + bar_height
            
            # Update bar
            self.canvas.coords(bar, x, y1, x + self.bar_width, y2)
            
            # Color based on level
            if display_level > 0.7:
                color = "#FF6B6B"  # Red
            elif display_level > 0.4:
                color = "#4ECDC4"  # Teal
            elif display_level > 0.1:
                color = "#3B8ED0"  # Blue
            else:
                color = "#555555"  # Gray
                
            self.canvas.itemconfig(bar, fill=color)
    
    def reset_waveform(self):
        """Reset waveform to idle state"""
        self.audio_levels.clear()
        for i in range(self.num_bars):
            self.audio_levels.append(0)
            
        for bar in self.waveform_bars:
            # Reset to flat line
            start_x = (self.canvas_width - (self.num_bars * (self.bar_width + self.bar_spacing) - self.bar_spacing)) // 2
            i = self.waveform_bars.index(bar)
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            self.canvas.coords(bar, x, self.canvas_height // 2 - 2, 
                             x + self.bar_width, self.canvas_height // 2 + 2)
            self.canvas.itemconfig(bar, fill="#3B8ED0")
    
    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y
    
    def drag_window(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f'+{x}+{y}')
    
    def setup_global_hotkey(self):
        """Set up global hotkey - with Wayland compatibility"""
        try:
            import os
            import subprocess
            
            # Check if we're on Wayland
            session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
            wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
            is_wayland = session_type == 'wayland' or wayland_display != ''
            
            if is_wayland:
                print("🔧 Detected Wayland session - setting up Wayland-compatible hotkey")
                self.setup_wayland_hotkey()
            else:
                print("🔧 Detected X11 session - using standard hotkey method")
                self.setup_x11_hotkey()
                
        except Exception as e:
            print(f"❌ Failed to set up hotkey listener: {e}")
            print("   Alternative: Use the Record button in the app")
    
    def setup_wayland_hotkey(self):
        """Set up Wayland-compatible global hotkey using D-Bus"""
        try:
            import subprocess
            import threading
            
            print("🔧 Setting up Wayland hotkey using system integration...")
            
            # Create a script that will be called by the system shortcut
            script_path = "/tmp/faststt_toggle.py"
            script_content = f'''#!/usr/bin/env python3
import socket
import sys
import os

# Send toggle signal to running FastSTT instance
try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/tmp/faststt_hotkey.sock")
    sock.send(b"toggle")
    sock.close()
    print("Toggle signal sent")
except Exception as e:
    print(f"Failed to send toggle signal: {{e}}")
    # Fallback: try to start the app if not running
    os.system("cd {os.getcwd()} && uv run python app_v4_simple.py &")
'''
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            
            # Set up socket server to receive hotkey signals
            self.setup_socket_server()
            
            # Try to register the hotkey with GNOME
            try:
                # Check if we're on GNOME
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                if 'gnome' in desktop:
                    self.setup_gnome_hotkey(script_path)
                else:
                    print("   Non-GNOME desktop detected - manual setup required")
                    self.print_manual_setup_instructions(script_path)
            except Exception as e:
                print(f"   Could not auto-setup system hotkey: {e}")
                self.print_manual_setup_instructions(script_path)
                
        except Exception as e:
            print(f"❌ Wayland hotkey setup failed: {e}")
            print("   Falling back to app-only hotkey (works when app is focused)")
            self.setup_fallback_hotkey()
    
    def setup_socket_server(self):
        """Set up Unix socket server to receive hotkey signals"""
        import socket
        import threading
        import os
        
        def socket_server():
            socket_path = "/tmp/faststt_hotkey.sock"
            
            # Remove existing socket if it exists
            try:
                os.unlink(socket_path)
            except OSError:
                pass
            
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.bind(socket_path)
                sock.listen(1)
                
                print("✅ Socket server listening for hotkey signals")
                
                while True:
                    try:
                        conn, addr = sock.accept()
                        data = conn.recv(1024)
                        if data == b"toggle":
                            print("🎯 Hotkey signal received via socket!")
                            self.after_idle(self.toggle_recording)
                        conn.close()
                    except Exception as e:
                        if hasattr(self, '_socket_server_running') and not self._socket_server_running:
                            break
                        print(f"Socket server error: {e}")
                        
            except Exception as e:
                print(f"Failed to start socket server: {e}")
        
        self._socket_server_running = True
        self.socket_thread = threading.Thread(target=socket_server, daemon=True)
        self.socket_thread.start()
    
    def setup_gnome_hotkey(self, script_path):
        """Try to automatically set up GNOME keyboard shortcut"""
        try:
            import subprocess
            
            # GNOME keyboard shortcut setup
            shortcut_name = "FastSTT Toggle"
            shortcut_command = f"python3 {script_path}"
            shortcut_key = "F8"
            
            # Try to set up the shortcut using gsettings
            subprocess.run([
                "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                "name", shortcut_name
            ], check=True)
            
            subprocess.run([
                "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                "command", shortcut_command
            ], check=True)
            
            subprocess.run([
                "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                "binding", shortcut_key
            ], check=True)
            
            # Add to the list of custom keybindings
            result = subprocess.run([
                "gsettings", "get", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings"
            ], capture_output=True, text=True)
            
            current_bindings = result.stdout.strip()
            if "faststt" not in current_bindings:
                if current_bindings == "@as []":
                    new_bindings = "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/']"
                else:
                    # Parse existing bindings and add ours
                    new_bindings = current_bindings.rstrip(']') + ", '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/']"
                
                subprocess.run([
                    "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings", new_bindings
                ], check=True)
            
            print("✅ GNOME keyboard shortcut set up successfully!")
            print(f"   F8 key will now toggle recording globally")
            
        except subprocess.CalledProcessError as e:
            print(f"   Failed to set up GNOME shortcut automatically: {e}")
            self.print_manual_setup_instructions(script_path)
        except Exception as e:
            print(f"   Error setting up GNOME shortcut: {e}")
            self.print_manual_setup_instructions(script_path)
    
    def print_manual_setup_instructions(self, script_path):
        """Print instructions for manual hotkey setup"""
        print("\n📋 Manual Setup Instructions:")
        print("   1. Open Settings → Keyboard → Keyboard Shortcuts")
        print("   2. Click 'Add Shortcut' or '+'")
        print("   3. Name: FastSTT Toggle")
        print(f"   4. Command: python3 {script_path}")
        print("   5. Shortcut: Press F8")
        print("   6. Click 'Add' or 'Save'")
        print("\n   Alternative: Use the Record button in the app window")
    
    def setup_x11_hotkey(self):
        """Set up X11-compatible global hotkey using pynput"""
        try:
            from pynput import keyboard
            from pynput.keyboard import Key
            
            def on_press(key):
                try:
                    if key == Key.f8:
                        print("🎯 F8 hotkey detected!")
                        self.after_idle(self.toggle_recording)
                except Exception as e:
                    print(f"Hotkey error: {e}")
            
            def on_release(key):
                if key == Key.esc:
                    print("ESC detected - hotkey listener is working")
            
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
                suppress=False
            )
            self.keyboard_listener.start()
            
            print("✅ X11 global hotkey listener started")
            if self.keyboard_listener.running:
                print("✅ Hotkey listener is running successfully")
            else:
                print("⚠️ Hotkey listener failed to start")
                
        except Exception as e:
            print(f"❌ Failed to start X11 keyboard listener: {e}")
            self.setup_fallback_hotkey()
    
    def setup_fallback_hotkey(self):
        """Fallback hotkey that only works when app is focused"""
        try:
            from pynput import keyboard
            from pynput.keyboard import Key
            
            def on_press(key):
                try:
                    if key == Key.f8:
                        print("🎯 F8 hotkey detected (app-focused only)!")
                        self.after_idle(self.toggle_recording)
                except Exception as e:
                    print(f"Hotkey error: {e}")
            
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                suppress=False
            )
            self.keyboard_listener.start()
            
            print("✅ Fallback hotkey active (works when app is focused)")
            
        except Exception as e:
            print(f"❌ Even fallback hotkey failed: {e}")
            print("   Use the Record button to control recording")
    
    def on_key_press(self, key):
        """Handle key press events (fallback method)"""
        # Fallback not needed for Ctrl+F8 combination
        pass
    
    def load_model(self):
        """Load Whisper model - using openai-whisper"""
        try:
            print(f"Loading model: {self.model_name}")
            self.after(0, lambda: self.status_label.configure(text="Loading model..."))

            # Check for FORCE_CPU environment variable
            force_cpu = os.environ.get("FORCE_CPU", "0") == "1"

            # Determine device
            if force_cpu:
                device = "cpu"
                print("⚠️ FORCE_CPU=1 - Using CPU mode")
            elif torch.cuda.is_available():
                device = "cuda"
                print("🔍 CUDA available - attempting GPU mode...")
            else:
                device = "cpu"
                print("⚠️ CUDA not available - using CPU mode")

            # Load model with openai-whisper (simpler API)
            print(f"Loading {self.model_name} on {device.upper()}...")
            self.model = whisper.load_model(self.model_name, device=device)
            self.device_used = device.upper()
            print(f"✅ Model loaded successfully on {self.device_used}")

            if device == "cuda":
                gpu_name = torch.cuda.get_device_name(0)
                print(f"   GPU: {gpu_name}")

            self.after(0, lambda: self.status_label.configure(text=f"Ready • {self.device_used}"))

            # DISABLED - Grammar tool initialization
            # threading.Thread(target=self.init_grammar_tool, daemon=True).start()

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
    
    def init_grammar_tool(self):
        """Initialize grammar correction tool (DISABLED - Not in use)"""
        # DISABLED - Grammar correction temporarily disabled
        print("⚠️ Grammar correction is disabled")
        self.grammar_correction = False
        self.grammar_tool = None
        return

        # OLD CODE - Commented out
        # try:
        #     print("🔧 Initializing grammar tool in background...")
        #     if os.environ.get("DISABLE_GRAMMAR", "0") == "1":
        #         print("⚠️ Grammar correction disabled via DISABLE_GRAMMAR=1")
        #         self.grammar_correction = False
        #         return
        #     self.grammar_tool = language_tool_python.LanguageTool('en-US')
        #     print("✅ Grammar tool ready!")
        # except Exception as e:
        #     print(f"⚠️ Grammar tool initialization failed: {e}")
        #     print("   Continuing without grammar correction")
        #     self.grammar_correction = False
    
    def toggle_recording(self):
        """Toggle recording state"""
        if self.model is None:
            print("Model not loaded yet!")
            return
            
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        
        # Update button
        self.record_button.configure(
            text="⏹ Stop",
            fg_color="#FF6B6B",
            hover_color="#CC5555"
        )
        
        # Update status
        self.status_label.configure(text="Recording...", text_color="red")
        
        # Clear audio
        self.audio_frames = []
        self.last_levels.clear()
        
        # Start recording
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        
        # Start audio monitoring
        self.audio_monitor_thread = threading.Thread(target=self.monitor_audio_level)
        self.audio_monitor_thread.start()
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        
        # Update button
        self.record_button.configure(
            text="🎤 Record",
            fg_color=["#3B8ED0", "#1F6AA5"],
            hover_color=["#36719F", "#144870"]
        )
        
        # Reset waveform
        self.reset_waveform()
        
        # Update status
        self.status_label.configure(text="Processing...", text_color="orange")
        
        # Wait for recording to finish
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join()
        
        # Process audio
        threading.Thread(target=self.process_audio, daemon=True).start()
    
    def record_audio(self):
        """Record audio from microphone"""
        print("🎧 Starting audio recording...")
        try:
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16') as stream:
                while self.is_recording:
                    audio_chunk, overflowed = stream.read(1024)
                    self.audio_frames.append(audio_chunk)
                    self.audio_level = np.abs(audio_chunk).mean()
        except Exception as e:
            print(f"Recording error: {e}")
            self.after(0, lambda: self.status_label.configure(text="Recording Error", text_color="red"))
    
    def monitor_audio_level(self):
        """Monitor audio level for waveform"""
        while self.is_recording:
            if self.audio_level > 0:
                self.after(0, lambda level=self.audio_level: self.update_waveform(level))
            time.sleep(0.05)  # 20 FPS
    
    def process_audio(self):
        """Process recorded audio"""
        if not self.audio_frames:
            self.after(0, lambda: self.status_label.configure(text="No audio", text_color="red"))
            return
        
        try:
            # Concatenate audio
            audio_data = np.concatenate(self.audio_frames, axis=0)
            
            # Save to WAV
            with wave.open(self.temp_wav_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())
            
            # Transcribe with openai-whisper
            print("🎯 Starting transcription...")
            self.after(0, lambda: self.status_label.configure(text="Transcribing...", text_color="yellow"))

            result = self.model.transcribe(self.temp_wav_file, fp16=(self.device_used == "CUDA"))

            transcription = result["text"].strip()
            print(f"🎤 Transcribed: '{transcription}'")
            
            if transcription:
                # Add punctuation first
                self.after(0, lambda: self.status_label.configure(text="Adding punctuation...", text_color="cyan"))
                punctuated_text = self.add_punctuation(transcription)
                print(f"📝 Punctuated: {punctuated_text}")

                # DISABLED - Grammar correction (skip this step)
                # if self.grammar_correction and self.grammar_tool:
                #     self.after(0, lambda: self.status_label.configure(text="Correcting grammar...", text_color="purple"))
                #     corrected_text = self.correct_grammar(punctuated_text)
                # else:
                #     corrected_text = punctuated_text

                # Use punctuated text directly (no grammar correction)
                corrected_text = punctuated_text

                # Insert immediately
                self.after(0, lambda: self.status_label.configure(text="Inserting...", text_color="green"))
                self.after(0, lambda: self.insert_text(corrected_text))
            else:
                self.after(0, lambda: self.status_label.configure(text="No speech", text_color="gray"))
                
        except Exception as e:
            print(f"Processing error: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
        finally:
            if os.path.exists(self.temp_wav_file):
                os.remove(self.temp_wav_file)
    
    def add_punctuation(self, text):
        """Add intelligent punctuation to text"""
        if not text:
            return text
            
        text = text.strip()
        
        # Add period at the end if no punctuation exists
        if not text.endswith(('.', '!', '?', ';', ':')):
            # Check for question words to add question mark
            question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose', 'whom']
            if any(text.lower().startswith(word) for word in question_words):
                text += '?'
            else:
                text += '.'
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Add commas before common conjunctions if missing
        text = re.sub(r'\s+(and|but|or|so|yet|for|nor)\s+', r', \1 ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
        
        return text
    
    def correct_grammar(self, text):
        """Apply grammar correction"""
        try:
            corrected = self.grammar_tool.correct(text)
            if corrected != text:
                print(f"Grammar: '{text}' → '{corrected}'")
            return corrected
        except Exception as e:
            print(f"Grammar error: {e}")
            return text
    
    def insert_text(self, text):
        """Insert text at cursor - works in terminals and all applications"""
        try:
            # Always copy to clipboard first
            pyperclip.copy(text)
            
            # Method 1: Try direct typing first (works in many cases including terminals)
            pyautogui.typewrite(text, interval=0.001)
            
            self.status_label.configure(text="Inserted!", text_color="green")
            print(f"✅ Inserted: {text} (also copied to clipboard)")
            
            # Reset status after 2 seconds
            self.after(2000, lambda: self.status_label.configure(
                text=f"Ready • {self.device_used}", 
                text_color="gray70"
            ))
        except Exception as e:
            # Fallback to clipboard method if typewrite fails
            try:
                print("Typewrite failed, trying clipboard method...")
                pyperclip.copy(text)
                time.sleep(0.1)
                
                import platform
                if platform.system() == 'Darwin':
                    pyautogui.hotkey('cmd', 'v')
                else:
                    # Try Ctrl+Shift+V first for terminals
                    pyautogui.hotkey('ctrl', 'shift', 'v')
                
                self.status_label.configure(text="Inserted!", text_color="green")
                print(f"✅ Inserted via clipboard: {text}")
                
                self.after(2000, lambda: self.status_label.configure(
                    text=f"Ready • {self.device_used}", 
                    text_color="gray70"
                ))
            except Exception as e2:
                print(f"Insert error: {e2}")
                self.status_label.configure(text="Insert failed", text_color="red")
    
    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        
        # Stop socket server
        if hasattr(self, '_socket_server_running'):
            self._socket_server_running = False
            try:
                import os
                os.unlink("/tmp/faststt_hotkey.sock")
            except:
                pass
        
        # Stop keyboard listener
        if hasattr(self, 'keyboard_listener'):
            try:
                self.keyboard_listener.stop()
                print("🛑 Hotkey listener stopped")
            except Exception as e:
                print(f"Error stopping hotkey listener: {e}")

        # DISABLED - Grammar tool cleanup (not using grammar tool)
        # if self.grammar_tool:
        #     try:
        #         self.grammar_tool.close()
        #     except:
        #         pass

        if os.path.exists(self.temp_wav_file):
            os.remove(self.temp_wav_file)
    
    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.destroy()


if __name__ == "__main__":
    app = SimpleApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()