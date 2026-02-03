# <img src="logo.png" width="48" align="center"> FastSimple 🎤

**AI-Powered Speech-to-Text with Grammar Correction & Multiple Tones**

FastSimple transcribes your voice and automatically types text at your cursor. It features AI-powered grammar correction and multiple writing tones using OpenAI Whisper, Ollama, and LanguageTool.

![Demo](demo.gif)

---

## ✨ Features

- 🎯 **Global Hotkey** - Press `F8` to start/stop recording from anywhere
- 🚀 **GPU Acceleration** - Automatic CUDA support (falls back to CPU)
- ✍️ **Grammar Correction** - Fix grammar and remove filler words
- 🎨 **Multiple Tones** - Original, Grammar, Professional, Polite, Rephrase
- ⚡ **Auto Insertion** - Text appears at your cursor automatically
- 🖥️ **Compact UI** - Small floating window with tone dropdown

---

## 🚀 Quick Start

### Windows

```batch
# 1. Setup (run once)
setup.bat

# 2. Run the app
run.bat                 # Basic version
run_grammer.bat         # Grammar correction
run_with_settings.bat   # Full version with tone dropdown
```

### Ubuntu

```bash
# 1. Setup (run once)
./setup.sh

# 2. Run the app
./run.sh                # Basic version
./run_grammer.sh        # Grammar correction
./run_with_settings.sh  # Full version with tone dropdown
```

Press **F8** to record. Speak. Press **F8** again to stop and insert text.

---

## 🎛️ Three App Versions

| File | Command (Win) | Command (Ubuntu) | Description |
|------|---------------|------------------|-------------|
| `app.py` | `run.bat` | `./run.sh` | Basic: Punctuation only |
| `app_with_grammer.py` | `run_grammer.bat` | `./run_grammer.sh` | Grammar correction via Ollama |
| `app_with_settings.py` | `run_with_settings.bat` | `./run_with_settings.sh` | Full: 5-tone dropdown menu |

### Writing Tones (Settings version)

| Tone | Description | Requires |
|------|-------------|----------|
| **Original** | Just punctuation | Nothing |
| **Grammar** | Grammar fix + filler removal | Java + LanguageTool |
| **Professional** | Grammar + simplify | Ollama |
| **Polite** | Courteous formal language | Ollama |
| **Rephrase** | Complete rewording | Ollama |

---

## 🪟 Windows Batch Files

| File | Purpose |
|------|---------|
| `setup.bat` | Install dependencies (run once) |
| `setup_cuda.bat` | Setup with CUDA GPU support |
| `run.bat` | Launch basic version |
| `run_grammer.bat` | Launch grammar version |
| `run_with_settings.bat` | Launch settings version with dropdown |
| `run_win.bat` | Alternative Windows launcher |
| `start.bat` | Quick start shortcut |
| `create_shortcuts.bat` | Create desktop shortcuts |
| `remove_shortcuts.bat` | Remove desktop shortcuts |

---

## 🔧 Optional: Setup Ollama (for AI Tones)

For Professional, Polite, and Rephrase tones:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull gemma3:latest

# Start Ollama
ollama serve
```

On Windows, download from [ollama.com](https://ollama.com).

---

## 🔧 Optional: Setup Java (for Grammar Tone)

For fast local grammar correction without Ollama:

```bash
# Ubuntu
sudo apt install default-jre

# Windows - download from java.com
```

---

## ⚙️ Configuration

### Force CPU Mode

**Windows:**
```batch
set FORCE_CPU=1
run.bat
```

**Ubuntu:**
```bash
FORCE_CPU=1 ./run.sh
```

### Change Ollama Model

**Windows:**
```batch
set OLLAMA_MODEL=llama3.2:3b
run_with_settings.bat
```

**Ubuntu:**
```bash
OLLAMA_MODEL=llama3.2:3b ./run_with_settings.sh
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Model not loaded yet!" | Wait 10-30 seconds on first start |
| "Ollama not available" | Run `ollama serve` and pull a model |
| "LanguageTool not available" | Install Java |
| No audio | Check microphone is default input |
| F8 not working (Wayland) | Use the Record button instead |

---

## 📋 Requirements

- **OS**: Windows 10/11 or Ubuntu 20.04+
- **Python**: 3.10+
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 5GB free space
- **GPU**: NVIDIA with CUDA (optional, for speed)

---

## 🏗️ Project Files

```
fast_simple/
├── app.py                      # Basic version
├── app_with_grammer.py         # Grammar version
├── app_with_settings.py        # Full version with dropdown
├── setup.bat / setup.sh        # Setup scripts
├── run.bat / run.sh            # Launch basic version
├── run_grammer.bat / run_grammer.sh      # Launch grammar version
├── run_with_settings.bat / run_with_settings.sh  # Launch settings version
├── ffmpeg.exe                  # Bundled for Windows
├── logo.png                    # Logo
├── demo.gif                    # Demo
└── README.md                   # This file
```

---

## 🧰 Tech Stack

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Ollama](https://ollama.com) - Local AI
- [LanguageTool](https://languagetool.org) - Grammar correction
- [PyTorch](https://pytorch.org/) - Deep learning
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - UI

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/AnandBhandari1/fast_simple/issues)

---

<div align="center">

[Report Bug](https://github.com/AnandBhandari1/fast_simple/issues) · [Request Feature](https://github.com/AnandBhandari1/fast_simple/issues)

</div>
