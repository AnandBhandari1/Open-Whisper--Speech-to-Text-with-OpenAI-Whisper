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


class VoiceTypeAI_Settings(ctk.CTk):
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
            fg_color="#1E1E1E",  # Dark gray background
            corner_radius=0,  # Square corners
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
            corner_radius=0,  # Square corners
            fg_color="#6200EE",
            hover_color="#3700B3",
            text_color="white",
        )
        self.record_button.place(x=10, y=10)

        # Tone dropdown label
        self.tone_label = ctk.CTkLabel(
            self.main_frame,
            text="Tone:",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
        )
        self.tone_label.place(x=70, y=12)

        # Tone dropdown - expanded options
        self.tone_options = ["Original", "Grammar", "Professional", "Polite", "Rephrase"]
        self.tone_var = ctk.StringVar(value="Original")
        self.tone_dropdown = ctk.CTkOptionMenu(
            self.main_frame,
            values=self.tone_options,
            variable=self.tone_var,
            command=self.on_tone_change,
            width=95,
            height=28,
            corner_radius=0,  # Square corners
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=11),
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#333333",
            dropdown_hover_color="#444444",
            dropdown_text_color="white",
        )
        self.tone_dropdown.place(x=70, y=30)

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

        # Current tone
        self.current_tone = "original"
        self.tone_colors = {
            "original": "#4CAF50",
            "grammar": "#2196F3",
            "professional": "#6200EE",
            "polite": "#E91E63",
            "rephrase": "#FF9800",
        }

        # Ollama settings
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "gemma3:latest")
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_available = False

        # LanguageTool settings (fast local grammar)
        self.language_tool = None
        self.language_tool_available = False

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

    def on_tone_change(self, choice):
        """Handle tone dropdown change"""
        self.current_tone = choice.lower()
        color = self.tone_colors[self.current_tone]
        print(f"[TONE] Changed to: {choice} ({color})")

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
    os.system("cd {os.getcwd()} && uv run python app_with_settings.py &")
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

            threading.Thread(target=self.init_ollama, daemon=True).start()
            threading.Thread(target=self.init_language_tool, daemon=True).start()
        except Exception as e:
            print(f"❌ Error loading model: {e}")

    def init_ollama(self):
        """Initialize Ollama connection"""
        try:
            import ollama
            print(f"🔧 Checking Ollama at {self.ollama_host}...")

            client = ollama.Client(host=self.ollama_host)
            models = client.list()
            model_names = [m.model for m in models.models] if models.models else []

            if self.ollama_model in model_names:
                print(f"[OK] Model '{self.ollama_model}' is available")
                self.ollama_available = True
            else:
                print(f"[WARNING] Model '{self.ollama_model}' not found")
                print(f"   Available: {', '.join(model_names[:5])}")
                for fallback in ["gemma3:latest", "llama3.2:3b", "gemma2:2b"]:
                    if fallback in model_names:
                        self.ollama_model = fallback
                        print(f"   Using fallback: {fallback}")
                        self.ollama_available = True
                        break
        except Exception as e:
            print(f"[WARNING] Ollama not available: {e}")
            self.ollama_available = False

    def init_language_tool(self):
        """Initialize LanguageTool for fast local grammar correction"""
        try:
            import language_tool_python
            print("🔧 Initializing LanguageTool...")
            self.language_tool = language_tool_python.LanguageTool('en-US')
            self.language_tool_available = True
            print("[OK] LanguageTool ready (fast grammar correction)")
        except Exception as e:
            print(f"[WARNING] LanguageTool not available: {e}")
            print("   Grammar tone will use fallback")
            self.language_tool_available = False

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
        """Process recorded audio with selected tone"""
        if not self.audio_frames:
            return

        try:
            self.record_button.configure(text="⏳", fg_color="#FF9800")
            self.update()

            audio_data = np.concatenate(self.audio_frames, axis=0)
            with wave.open(self.temp_wav_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())

            print(f"[TRANSCRIBE] Tone: {self.current_tone.upper()}")
            result = self.model.transcribe(
                self.temp_wav_file, fp16=(self.device_used == "CUDA")
            )
            transcription = result["text"].strip()
            print(f"[TEXT] Raw: '{transcription}'")

            if transcription:
                if self.current_tone == "original":
                    final_text = self.add_punctuation(transcription)
                    print(f"[TEXT] Original: {final_text}")
                elif self.current_tone == "grammar":
                    final_text = self.process_grammar(transcription)
                    print(f"[TEXT] Grammar: {final_text}")
                elif self.ollama_available:
                    if self.current_tone == "professional":
                        final_text = self.process_professional(transcription)
                    elif self.current_tone == "polite":
                        final_text = self.process_polite(transcription)
                    else:  # rephrase
                        final_text = self.process_rephrase(transcription)
                    print(f"[TEXT] {self.current_tone.capitalize()}: {final_text}")
                else:
                    final_text = self.add_punctuation(transcription)
                    print("[WARNING] Ollama not available, using original mode")

                self.insert_text(final_text)
            else:
                self.record_button.configure(text="🎙", fg_color="#6200EE")

        except Exception as e:
            print(f"Processing error: {e}")
            self.record_button.configure(text="❌", fg_color="#6200EE")
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

    def process_professional(self, text):
        """Process text with professional tone"""
        punctuated = self.add_punctuation(text)
        return self.call_ollama(punctuated, "professional")

    def process_polite(self, text):
        """Process text with polite tone"""
        punctuated = self.add_punctuation(text)
        return self.call_ollama(punctuated, "polite")

    def process_grammar(self, text):
        """Process text with fast grammar correction using LanguageTool"""
        punctuated = self.add_punctuation(text)
        
        if not self.language_tool_available:
            print("[WARNING] LanguageTool not available, using punctuation only")
            return punctuated
        
        try:
            print("[GRAMMAR] Using LanguageTool...")
            matches = self.language_tool.check(punctuated)
            corrected = self.language_tool.correct(punctuated)
            
            # Remove filler words that LanguageTool might miss
            fillers = ['um,', 'uh,', 'like,', 'you know,', 'i mean,', 'basically,', 
                       'actually,', 'literally,', 'so,', 'well,', 'right,', 'okay,',
                       ' um ', ' uh ', ' like ', ' you know ', ' i mean ', 
                       ' basically ', ' actually ', ' literally ', ' right ', ' okay ']
            
            result = corrected
            for filler in fillers:
                result = re.sub(filler, ' ', result, flags=re.IGNORECASE)
            
            # Clean up extra spaces
            result = re.sub(r'\s+', ' ', result).strip()
            
            return result if result else punctuated
            
        except Exception as e:
            print(f"[WARNING] LanguageTool error: {e}")
            return punctuated

    def process_rephrase(self, text):
        """Process text with rephrase tone"""
        punctuated = self.add_punctuation(text)
        return self.call_ollama(punctuated, "rephrase")

    def call_ollama(self, text, mode):
        """Call Ollama with appropriate prompt based on mode"""
        try:
            import ollama

            if mode == "professional":
                system_prompt = """You are a professional transcription editor. Clean up transcribed speech by fixing grammar, removing filler words, and simplifying while keeping the core meaning.

Rules:
1. Remove filler words: um, uh, like, you know, I mean, basically, actually, literally, so, well, right, okay
2. Fix grammar and spelling errors
3. Add proper punctuation where needed
4. Simplify the text - make it concise and straightforward
5. Remove redundant or repetitive phrases
6. Keep the original meaning intact
7. Do not add explanations or comments
8. Output ONLY the cleaned text, nothing else

Example:
Input: "Um, so like I was thinking that maybe we should uh go to the store"
Output: "We should go to the store."""
            elif mode == "polite":
                system_prompt = """You are a professional communication assistant. Convert the given text into polite, respectful, and courteous language suitable for formal or professional contexts.

Rules:
1. Remove filler words: um, uh, like, you know, I mean, basically, actually, literally, so, well, right, okay
2. Use polite phrases: "would you mind," "could you please," "I would appreciate if," "thank you for"
3. Soften direct commands into requests
4. Add courteous openings and closings where appropriate
5. Use formal vocabulary instead of casual expressions
6. Maintain the original intent but express it respectfully
7. Do not add explanations or comments
8. Output ONLY the polite version, nothing else

Example:
Input: "Send me the report by tomorrow"
Output: "Would you mind sending me the report by tomorrow? Thank you."

Input: "I need you to fix this bug now"
Output: "Could you please look into this bug when you have a moment? I would appreciate your help."""
            else:  # rephrase
                system_prompt = """You are a skilled writer who rephrases text for maximum clarity and impact. Rewrite the given text to make it clearer, more concise, and better structured.

Rules:
1. Rephrase sentences for better flow and readability
2. Use clearer and more precise vocabulary
3. Restructure awkward phrasing
4. Keep the original meaning but express it better
5. Vary sentence structure to make it more engaging
6. Remove redundancy and wordiness
7. Do not add explanations or comments
8. Output ONLY the rephrased text, nothing else

Example:
Input: "I was thinking that maybe we should consider going to the store because we need some milk"
Output: "Let's head to the store; we're out of milk."

Input: "The reason why I'm late is because there was a lot of traffic on the road"
Output: "Traffic delayed my arrival."""

            print(f"[OLLAMA] Sending to {self.ollama_model} ({mode} mode)...")
            client = ollama.Client(host=self.ollama_host)
            response = client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Text to process:\n\n{text}"},
                ],
                options={
                    "temperature": 0.3 if mode == "professional" else 0.5,
                    "num_predict": 300,
                },
            )

            result = response.message.content.strip()
            result = re.sub(r'^["\']+|["\']+$', '', result)
            result = result.strip()
            return result if result else text

        except Exception as e:
            print(f"[WARNING] Ollama call failed: {e}")
            return text

    def insert_text(self, text):
        """Insert text at cursor"""
        try:
            pyperclip.copy(text)
            pyautogui.typewrite(text, interval=0.001)
            print(f"[OK] Inserted: {text}")
            self.after(500, lambda: self.record_button.configure(text="🎙", fg_color="#6200EE"))
        except Exception as e:
            print(f"Insert error: {e}")
            self.record_button.configure(text="🎙", fg_color="#6200EE")

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
    app = VoiceTypeAI_Settings()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
