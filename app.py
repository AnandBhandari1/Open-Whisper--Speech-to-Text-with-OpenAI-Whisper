import os
import random
import re
import sys
import threading
import time
import tkinter as tk
import wave
from collections import deque

import customtkinter as ctk
import numpy as np

# import language_tool_python  # DISABLED - Grammar correction temporarily disabled
import pyautogui
import pyperclip
import sounddevice as sd
import torch
from pynput import keyboard
from pynput.keyboard import Key

# Configure ffmpeg path for whisper (use local bundled version)
try:
    import shutil

    import imageio_ffmpeg

    ffmpeg_bundled = imageio_ffmpeg.get_ffmpeg_exe()

    # Create a local copy named ffmpeg.exe if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_local = os.path.join(script_dir, "ffmpeg.exe")

    if not os.path.exists(ffmpeg_local):
        print("Creating local ffmpeg.exe copy...")
        shutil.copy2(ffmpeg_bundled, ffmpeg_local)

    # Add local directory to PATH so whisper can find ffmpeg.exe
    if script_dir not in os.environ["PATH"]:
        os.environ["PATH"] = script_dir + os.pathsep + os.environ["PATH"]

    print(f"[OK] Using bundled ffmpeg: {ffmpeg_local}")
except ImportError:
    print("[WARNING] imageio-ffmpeg not found, using system ffmpeg")
except Exception as e:
    print(f"[WARNING] Error setting up bundled ffmpeg: {e}")
    print("  Falling back to system ffmpeg")

import whisper  # Import after setting up ffmpeg


class SimpleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Create frameless circular window
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#000000")  # Make black transparent

        # Set circular button size (Android FAB standard is 56px)
        self.button_size = 64
        self.waveform_size = 120
        self.geometry(f"{self.waveform_size}x{self.waveform_size}")

        # Make window draggable
        self.bind("<Button-1>", self.click_window)
        self.bind("<B1-Motion>", self.drag_window)

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Get screen dimensions first
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Position in bottom right corner - only set once
        x = screen_width - self.waveform_size - 40
        y = screen_height - self.waveform_size - 40
        self.geometry(f"+{x}+{y}")

        # Main frame - will hold waveform and button
        self.main_frame = ctk.CTkFrame(
            self,
            width=self.waveform_size,
            height=self.waveform_size,
            fg_color="transparent",
        )
        self.main_frame.pack(fill="both", expand=True)

        # Waveform canvas (circular around button)
        self.canvas = ctk.CTkCanvas(
            self.main_frame,
            width=self.waveform_size,
            height=self.waveform_size,
            bg="#000000",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Circular record button (FAB style)
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text="🎙",
            command=self.toggle_recording,
            font=ctk.CTkFont(size=24),
            width=self.button_size - 8,
            height=self.button_size - 8,
            corner_radius=(self.button_size - 8) // 2,
            fg_color="#6200EE",  # Material Design primary
            hover_color="#3700B3",
            text_color="white",
        )
        self.record_button.place(relx=0.5, rely=0.5, anchor="center")

        # Waveform parameters - simple circular bars
        self.num_waveform_bars = 12
        self.waveform_bars = []
        self.wavebar_radius = 40  # Distance from center
        self.wavebar_length = 10  # Initial length
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
        self.grammar_correction = (
            False  # DISABLED - Grammar correction temporarily disabled
        )
        self.immediate_insert = True

        # Initialize grammar tool
        self.grammar_tool = None  # DISABLED - Not using grammar correction

        # Global hotkey
        self.hotkey = Key.f8
        self.setup_global_hotkey()

        # Load model
        self.model = None
        threading.Thread(target=self.load_model, daemon=True).start()

        # Start waveform animation check
        self.update_waveform_animation()

    def init_waveform(self):
        """Initialize circular waveform bars around button"""
        self.waveform_bars = []

        center_x = self.waveform_size // 2
        center_y = self.waveform_size // 2

        for i in range(self.num_waveform_bars):
            angle = (2 * np.pi * i) / self.num_waveform_bars

            # Calculate bar position
            x1 = center_x + self.wavebar_radius * np.cos(angle)
            y1 = center_y + self.wavebar_radius * np.sin(angle)
            x2 = center_x + (self.wavebar_radius + self.wavebar_length) * np.cos(angle)
            y2 = center_y + (self.wavebar_radius + self.wavebar_length) * np.sin(angle)

            # Create bar
            bar = self.canvas.create_line(
                x1, y1, x2, y2, fill="#6200EE", width=3, capstyle=tk.ROUND
            )
            self.waveform_bars.append(bar)

    def update_waveform_animation(self):
        """Update waveform bars based on audio level when recording"""
        if self.is_recording and hasattr(self, "audio_level"):
            # Normalize audio level
            normalized_level = min(self.audio_level / 3000, 1.0)

            # Add smoothing
            self.last_levels.append(normalized_level)
            smooth_level = sum(self.last_levels) / len(self.last_levels)

            center_x = self.waveform_size // 2
            center_y = self.waveform_size // 2

            for i, bar in enumerate(self.waveform_bars):
                angle = (2 * np.pi * i) / self.num_waveform_bars

                # Dynamic bar length based on audio level
                bar_extension = smooth_level * 20  # Max 20 pixels extension
                current_length = self.wavebar_length + bar_extension

                # Add some variation for natural look
                variation = 1 + 0.3 * np.sin(time.time() * 10 + i * 0.5)
                current_length *= variation

                # Calculate bar position
                x1 = center_x + self.wavebar_radius * np.cos(angle)
                y1 = center_y + self.wavebar_radius * np.sin(angle)
                x2 = center_x + (self.wavebar_radius + current_length) * np.cos(angle)
                y2 = center_y + (self.wavebar_radius + current_length) * np.sin(angle)

                # Update bar
                self.canvas.coords(bar, x1, y1, x2, y2)

                # Color based on level
                if smooth_level > 0.6:
                    color = "#FF1744"  # Red
                elif smooth_level > 0.3:
                    color = "#FF9800"  # Orange
                else:
                    color = "#6200EE"  # Purple

                self.canvas.itemconfig(bar, fill=color)
        else:
            # Reset to default
            center_x = self.waveform_size // 2
            center_y = self.waveform_size // 2

            for i, bar in enumerate(self.waveform_bars):
                angle = (2 * np.pi * i) / self.num_waveform_bars

                x1 = center_x + self.wavebar_radius * np.cos(angle)
                y1 = center_y + self.wavebar_radius * np.sin(angle)
                x2 = center_x + (self.wavebar_radius + self.wavebar_length) * np.cos(
                    angle
                )
                y2 = center_y + (self.wavebar_radius + self.wavebar_length) * np.sin(
                    angle
                )

                self.canvas.coords(bar, x1, y1, x2, y2)
                self.canvas.itemconfig(bar, fill="#6200EE")

        self.after(50, self.update_waveform_animation)

    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_window(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def setup_global_hotkey(self):
        """Set up global hotkey - with Wayland compatibility"""
        try:
            import os
            import subprocess

            # Check if we're on Wayland
            session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
            wayland_display = os.environ.get("WAYLAND_DISPLAY", "")
            is_wayland = session_type == "wayland" or wayland_display != ""

            if is_wayland:
                print(
                    "[INFO] Detected Wayland session - setting up Wayland-compatible hotkey"
                )
                self.setup_wayland_hotkey()
            else:
                print("[INFO] Detected X11 session - using standard hotkey method")
                self.setup_x11_hotkey()

        except Exception as e:
            print(f"❌ Failed to set up hotkey listener: {e}")
            print("   Alternative: Use the Record button in the app")

    def setup_wayland_hotkey(self):
        """Set up Wayland-compatible global hotkey using D-Bus"""
        try:
            import subprocess
            import threading

            print("[INFO] Setting up Wayland hotkey using system integration...")

            # Create a script that will be called by the system shortcut
            script_path = "/tmp/faststt_toggle.py"
            script_content = f"""#!/usr/bin/env python3
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
"""

            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)

            # Set up socket server to receive hotkey signals
            self.setup_socket_server()

            # Try to register the hotkey with GNOME
            try:
                # Check if we're on GNOME
                desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
                if "gnome" in desktop:
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
        import os
        import socket
        import threading

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

                print("[OK] Socket server listening for hotkey signals")

                while True:
                    try:
                        conn, addr = sock.accept()
                        data = conn.recv(1024)
                        if data == b"toggle":
                            print("[F8] Hotkey signal received via socket!")
                            self.after_idle(self.toggle_recording)
                        conn.close()
                    except Exception as e:
                        if (
                            hasattr(self, "_socket_server_running")
                            and not self._socket_server_running
                        ):
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
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                    "name",
                    shortcut_name,
                ],
                check=True,
            )

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                    "command",
                    shortcut_command,
                ],
                check=True,
            )

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/",
                    "binding",
                    shortcut_key,
                ],
                check=True,
            )

            # Add to the list of custom keybindings
            result = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.settings-daemon.plugins.media-keys",
                    "custom-keybindings",
                ],
                capture_output=True,
                text=True,
            )

            current_bindings = result.stdout.strip()
            if "faststt" not in current_bindings:
                if current_bindings == "@as []":
                    new_bindings = "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/']"
                else:
                    # Parse existing bindings and add ours
                    new_bindings = (
                        current_bindings.rstrip("]")
                        + ", '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/faststt/']"
                    )

                subprocess.run(
                    [
                        "gsettings",
                        "set",
                        "org.gnome.settings-daemon.plugins.media-keys",
                        "custom-keybindings",
                        new_bindings,
                    ],
                    check=True,
                )

            print("[OK] GNOME keyboard shortcut set up successfully!")
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
                        print("[F8] F8 hotkey detected!")
                        self.after_idle(self.toggle_recording)
                except Exception as e:
                    print(f"Hotkey error: {e}")

            def on_release(key):
                if key == Key.esc:
                    print("ESC detected - hotkey listener is working")

            self.keyboard_listener = keyboard.Listener(
                on_press=on_press, on_release=on_release, suppress=False
            )
            self.keyboard_listener.start()

            print("[OK] X11 global hotkey listener started")
            if self.keyboard_listener.running:
                print("[OK] Hotkey listener is running successfully")
            else:
                print("[WARNING] Hotkey listener failed to start")

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
                        print("[F8] F8 hotkey detected (app-focused only)!")
                        self.after_idle(self.toggle_recording)
                except Exception as e:
                    print(f"Hotkey error: {e}")

            self.keyboard_listener = keyboard.Listener(
                on_press=on_press, suppress=False
            )
            self.keyboard_listener.start()

            print("[OK] Fallback hotkey active (works when app is focused)")

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
                print("[WARNING] FORCE_CPU=1 - Using CPU mode")
            elif torch.cuda.is_available():
                device = "cuda"
                print("🔍 CUDA available - attempting GPU mode...")
            else:
                device = "cpu"
                print("[WARNING] CUDA not available - using CPU mode")

            # Load model with openai-whisper (simpler API)
            print(f"Loading {self.model_name} on {device.upper()}...")
            self.model = whisper.load_model(self.model_name, device=device)
            self.device_used = device.upper()
            print(f"[OK] Model loaded successfully on {self.device_used}")

            if device == "cuda":
                gpu_name = torch.cuda.get_device_name(0)
                print(f"   GPU: {gpu_name}")

            self.after(
                0,
                lambda: self.status_label.configure(text=f"Ready • {self.device_used}"),
            )

            # DISABLED - Grammar tool initialization
            # threading.Thread(target=self.init_grammar_tool, daemon=True).start()

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback

            traceback.print_exc()
            self.after(
                0, lambda: self.status_label.configure(text="Error", text_color="red")
            )

    def init_grammar_tool(self):
        """Initialize grammar correction tool (DISABLED - Not in use)"""
        # DISABLED - Grammar correction temporarily disabled
        print("[WARNING] Grammar correction is disabled")
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

        # Update button - red stop icon
        self.record_button.configure(
            text="⏹",
            fg_color="#FF1744",  # Material Design red
            hover_color="#D50000",
        )

        # Clear audio
        self.audio_frames = []
        self.last_levels.clear()

        # Start recording
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

        # Start audio monitoring (just for level detection, no visualization)
        self.audio_monitor_thread = threading.Thread(target=self.monitor_audio_level)
        self.audio_monitor_thread.start()

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False

        # Update button - back to mic icon
        self.record_button.configure(
            text="🎙",
            fg_color="#6200EE",
            hover_color="#3700B3",
        )

        # Wait for recording to finish
        if hasattr(self, "recording_thread"):
            self.recording_thread.join()

        # Process audio
        threading.Thread(target=self.process_audio, daemon=True).start()

    def record_audio(self):
        """Record audio from microphone"""
        print("[REC] Starting audio recording...")
        try:
            with sd.InputStream(
                samplerate=self.samplerate, channels=self.channels, dtype="int16"
            ) as stream:
                while self.is_recording:
                    audio_chunk, overflowed = stream.read(1024)
                    self.audio_frames.append(audio_chunk)
                    self.audio_level = np.abs(audio_chunk).mean()
        except Exception as e:
            print(f"Recording error: {e}")
            self.after(
                0,
                lambda: self.status_label.configure(
                    text="Recording Error", text_color="red"
                ),
            )

    def monitor_audio_level(self):
        """Monitor audio level for waveform visualization"""
        while self.is_recording:
            if self.audio_level > 0:
                # Audio level is tracked by record_audio, waveform animation handles visualization
                pass
            time.sleep(0.05)  # 20 FPS

    def process_audio(self):
        """Process recorded audio"""
        if not self.audio_frames:
            return

        try:
            # Show processing state
            self.after(
                0, lambda: self.record_button.configure(text="⏳", fg_color="#FF9800")
            )

            # Concatenate audio
            audio_data = np.concatenate(self.audio_frames, axis=0)

            # Save to WAV
            with wave.open(self.temp_wav_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())

            # Transcribe with openai-whisper
            print("[TRANSCRIBE] Starting transcription...")

            result = self.model.transcribe(
                self.temp_wav_file, fp16=(self.device_used == "CUDA")
            )

            transcription = result["text"].strip()
            print(f"[TEXT] Transcribed: '{transcription}'")

            if transcription:
                # Add punctuation
                punctuated_text = self.add_punctuation(transcription)
                print(f"[TEXT] Punctuated: {punctuated_text}")

                # Grammar correction (disabled)
                corrected_text = punctuated_text

                # Insert immediately
                self.after(0, lambda: self.insert_text(corrected_text))
            else:
                self.after(
                    0,
                    lambda: self.record_button.configure(text="🎙", fg_color="#6200EE"),
                )

        except Exception as e:
            print(f"Processing error: {e}")
            self.after(
                0, lambda: self.record_button.configure(text="❌", fg_color="#6200EE")
            )
        finally:
            if os.path.exists(self.temp_wav_file):
                os.remove(self.temp_wav_file)

    def add_punctuation(self, text):
        """Add intelligent punctuation to text"""
        if not text:
            return text

        text = text.strip()

        # Add period at the end if no punctuation exists
        if not text.endswith((".", "!", "?", ";", ":")):
            # Check for question words to add question mark
            question_words = [
                "what",
                "how",
                "why",
                "when",
                "where",
                "who",
                "which",
                "whose",
                "whom",
            ]
            if any(text.lower().startswith(word) for word in question_words):
                text += "?"
            else:
                text += "."

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        # Add commas before common conjunctions if missing
        text = re.sub(r"\s+(and|but|or|so|yet|for|nor)\s+", r", \1 ", text)

        # Fix spacing around punctuation
        text = re.sub(r"\s+([.!?])", r"\1", text)  # Remove space before punctuation
        text = re.sub(
            r"([.!?])([A-Za-z])", r"\1 \2", text
        )  # Add space after punctuation

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

            print(f"[OK] Inserted: {text} (also copied to clipboard)")

            # Reset button to mic icon after 1 second
            self.after(
                1000, lambda: self.record_button.configure(text="🎙", fg_color="#6200EE")
            )

        except Exception as e:
            # Fallback to clipboard method if typewrite fails
            try:
                print("Typewrite failed, trying clipboard method...")
                pyperclip.copy(text)
                time.sleep(0.1)

                import platform

                if platform.system() == "Darwin":
                    pyautogui.hotkey("cmd", "v")
                else:
                    # Try Ctrl+Shift+V first for terminals
                    pyautogui.hotkey("ctrl", "shift", "v")

                print(f"[OK] Inserted via clipboard: {text}")

                self.after(
                    1000,
                    lambda: self.record_button.configure(text="🎙", fg_color="#6200EE"),
                )

            except Exception as e2:
                print(f"Insert error: {e2}")
                self.after(
                    1000,
                    lambda: self.record_button.configure(text="🎙", fg_color="#6200EE"),
                )

    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False

        # Stop socket server
        if hasattr(self, "_socket_server_running"):
            self._socket_server_running = False
            try:
                os.unlink("/tmp/faststt_hotkey.sock")
            except:
                pass

        # Stop keyboard listener
        if hasattr(self, "keyboard_listener"):
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
