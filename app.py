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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_local = os.path.join(script_dir, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_local):
        shutil.copy2(ffmpeg_bundled, ffmpeg_local)
    if script_dir not in os.environ["PATH"]:
        os.environ["PATH"] = script_dir + os.pathsep + os.environ["PATH"]
    print(f"[OK] Using bundled ffmpeg: {ffmpeg_local}")
except ImportError:
    print("[WARNING] imageio-ffmpeg not found, using system ffmpeg")
except Exception as e:
    print(f"[WARNING] Error setting up bundled ffmpeg: {e}")

import whisper  # Import after setting up ffmpeg


class VoiceTypeAI_Original(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup - frameless floating window
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#000000")

        # Window size - compact rectangular
        self.window_width = 180
        self.window_height = 70
        self.geometry(f"{self.window_width}x{self.window_height}")

        # Draggable window
        self.bind("<Button-1>", self.click_window)
        self.bind("<B1-Motion>", self.drag_window)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Position in bottom right with margin
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - self.window_width - 60  # 60px from right edge
        y = screen_height - self.window_height - 80  # 80px from bottom edge
        self.geometry(f"+{x}+{y}")

        # Main frame - rectangular background
        self.main_frame = ctk.CTkFrame(
            self,
            width=self.window_width,
            height=self.window_height,
            fg_color="#1E1E1E",
            corner_radius=0,
            border_width=1,
            border_color="#333333",
        )
        self.main_frame.pack(fill="both", expand=True)

        # Recording button (square mic button)
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text="🎙",
            command=self.toggle_recording,
            font=ctk.CTkFont(size=18),
            width=50,
            height=50,
            corner_radius=0,
            fg_color="#6200EE",
            hover_color="#3700B3",
            text_color="white",
        )
        self.record_button.place(x=10, y=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        self.status_label.place(x=70, y=15)

        # Mode label
        self.mode_label = ctk.CTkLabel(
            self.main_frame,
            text="Original Only",
            font=ctk.CTkFont(size=10),
            text_color="#4CAF50",
        )
        self.mode_label.place(x=70, y=38)

        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.samplerate = 44100
        self.channels = 1
        self.temp_wav_file = "temp_audio.wav"
        self.audio_level = 0
        self.last_levels = deque(maxlen=5)

        # Model settings
        self.model_name = "large-v3-turbo"
        self.model = None
        self.device_used = "CPU"

        # Hotkey
        self.hotkey = Key.f8
        self.setup_global_hotkey()

        # Load model
        threading.Thread(target=self.load_model, daemon=True).start()

    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_window(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def setup_global_hotkey(self):
        """Set up global hotkey"""
        try:
            session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
            wayland_display = os.environ.get("WAYLAND_DISPLAY", "")
            is_wayland = session_type == "wayland" or wayland_display != ""

            if is_wayland:
                self.setup_wayland_hotkey()
            else:
                self.setup_x11_hotkey()
        except Exception as e:
            print(f"❌ Failed to set up hotkey listener: {e}")
            self.setup_fallback_hotkey()

    def setup_wayland_hotkey(self):
        """Set up Wayland-compatible global hotkey"""
        try:
            import socket
            script_path = "/tmp/faststt_toggle.py"
            script_content = f"""#!/usr/bin/env python3
import socket
import os
try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/tmp/faststt_hotkey.sock")
    sock.send(b"toggle")
    sock.close()
except Exception as e:
    os.system("cd {os.getcwd()} && uv run python app.py &")
"""
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            self.setup_socket_server()
        except Exception as e:
            print(f"❌ Wayland hotkey setup failed: {e}")
            self.setup_fallback_hotkey()

    def setup_socket_server(self):
        """Set up Unix socket server"""
        import socket

        def socket_server():
            socket_path = "/tmp/faststt_hotkey.sock"
            try:
                os.unlink(socket_path)
            except OSError:
                pass
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.bind(socket_path)
                sock.listen(1)
                while True:
                    try:
                        conn, addr = sock.accept()
                        data = conn.recv(1024)
                        if data == b"toggle":
                            self.after_idle(self.toggle_recording)
                        conn.close()
                    except:
                        break
            except Exception as e:
                print(f"Socket server error: {e}")

        self._socket_server_running = True
        self.socket_thread = threading.Thread(target=socket_server, daemon=True)
        self.socket_thread.start()

    def setup_x11_hotkey(self):
        """Set up X11-compatible global hotkey"""
        try:
            def on_press(key):
                if key == Key.f8:
                    self.after_idle(self.toggle_recording)

            self.keyboard_listener = keyboard.Listener(on_press=on_press, suppress=False)
            self.keyboard_listener.start()
            print("[OK] Global hotkey listener started (F8)")
        except Exception as e:
            print(f"❌ Failed to start X11 keyboard listener: {e}")
            self.setup_fallback_hotkey()

    def setup_fallback_hotkey(self):
        """Fallback hotkey that only works when app is focused"""
        try:
            def on_press(key):
                if key == Key.f8:
                    self.after_idle(self.toggle_recording)

            self.keyboard_listener = keyboard.Listener(on_press=on_press, suppress=False)
            self.keyboard_listener.start()
            print("[OK] App-focused hotkey active (F8)")
        except Exception as e:
            print(f"❌ Hotkey setup failed: {e}")

    def load_model(self):
        """Load Whisper model"""
        try:
            print(f"Loading model: {self.model_name}")
            force_cpu = os.environ.get("FORCE_CPU", "0") == "1"

            if force_cpu:
                device = "cpu"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"

            self.model = whisper.load_model(self.model_name, device=device)
            self.device_used = device.upper()
            print(f"[OK] Model loaded on {self.device_used}")

            if device == "cuda":
                print(f"   GPU: {torch.cuda.get_device_name(0)}")

            self.after(0, lambda: self.status_label.configure(text="Ready ✓"))
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error!", text_color="#FF1744"))

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
        self.record_button.configure(
            text="⏹",
            fg_color="#FF1744",
            hover_color="#D50000",
        )
        self.status_label.configure(text="Recording...", text_color="#FF1744")
        self.audio_frames = []
        self.last_levels.clear()
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        self.audio_monitor_thread = threading.Thread(target=self.monitor_audio_level)
        self.audio_monitor_thread.start()

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.record_button.configure(
            text="🎙",
            fg_color="#6200EE",
            hover_color="#3700B3",
        )
        self.status_label.configure(text="Processing...", text_color="#FF9800")
        if hasattr(self, "recording_thread"):
            self.recording_thread.join()
        threading.Thread(target=self.process_audio, daemon=True).start()

    def record_audio(self):
        """Record audio from microphone"""
        print("[REC] Starting audio recording...")
        try:
            with sd.InputStream(
                samplerate=self.samplerate, channels=self.channels, dtype="int16"
            ) as stream:
                while self.is_recording:
                    audio_chunk, _ = stream.read(1024)
                    self.audio_frames.append(audio_chunk)
                    self.audio_level = np.abs(audio_chunk).mean()
        except Exception as e:
            print(f"Recording error: {e}")

    def monitor_audio_level(self):
        """Monitor audio level"""
        while self.is_recording:
            time.sleep(0.05)

    def process_audio(self):
        """Process recorded audio"""
        if not self.audio_frames:
            return

        try:
            audio_data = np.concatenate(self.audio_frames, axis=0)
            with wave.open(self.temp_wav_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())

            print("[TRANSCRIBE] Starting transcription...")
            result = self.model.transcribe(
                self.temp_wav_file, fp16=(self.device_used == "CUDA")
            )
            transcription = result["text"].strip()
            print(f"[TEXT] Raw: '{transcription}'")

            if transcription:
                final_text = self.add_punctuation(transcription)
                print(f"[TEXT] Final: {final_text}")
                self.insert_text(final_text)
            else:
                self.record_button.configure(text="🎙", fg_color="#6200EE")
                self.status_label.configure(text="Ready", text_color="#888888")

        except Exception as e:
            print(f"Processing error: {e}")
            self.record_button.configure(text="❌", fg_color="#6200EE")
            self.status_label.configure(text="Error!", text_color="#FF1744")
        finally:
            if os.path.exists(self.temp_wav_file):
                os.remove(self.temp_wav_file)

    def add_punctuation(self, text):
        """Add intelligent punctuation to text"""
        if not text:
            return text

        text = text.strip()
        if not text.endswith((".", "!", "?", ";", ":")):
            question_words = ["what", "how", "why", "when", "where", "who", "which", "whose", "whom"]
            if any(text.lower().startswith(word) for word in question_words):
                text += "?"
            else:
                text += "."
        text += " "
        if text:
            text = text[0].upper() + text[1:]
        text = re.sub(r"\s+(and|but|or|so|yet|for|nor)\s+", r", \1 ", text)
        text = re.sub(r"\s+([.!?])", r"\1", text)
        text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)
        return text

    def insert_text(self, text):
        """Insert text at cursor"""
        try:
            pyperclip.copy(text)
            pyautogui.typewrite(text, interval=0.001)
            print(f"[OK] Inserted: {text}")
            self.after(500, lambda: [
                self.record_button.configure(text="🎙", fg_color="#6200EE"),
                self.status_label.configure(text="Ready", text_color="#888888"),
            ])
        except Exception as e:
            print(f"Insert error: {e}")
            self.record_button.configure(text="🎙", fg_color="#6200EE")
            self.status_label.configure(text="Ready", text_color="#888888")

    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        if hasattr(self, "_socket_server_running"):
            self._socket_server_running = False
            try:
                os.unlink("/tmp/faststt_hotkey.sock")
            except:
                pass
        if hasattr(self, "keyboard_listener"):
            try:
                self.keyboard_listener.stop()
            except:
                pass
        if os.path.exists(self.temp_wav_file):
            os.remove(self.temp_wav_file)

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.destroy()


if __name__ == "__main__":
    app = VoiceTypeAI_Original()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
