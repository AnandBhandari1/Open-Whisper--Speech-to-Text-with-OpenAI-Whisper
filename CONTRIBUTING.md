# Contributing to FastSimple

First off, thank you for considering contributing to FastSimple! It's people like you that make FastSimple such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by basic principles of respect and collaboration. By participating, you are expected to uphold this standard.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** and explain what's wrong with it
* **Explain which behavior you expected to see instead and why**
* **Include screenshots or animated GIFs** if possible
* **Include your system information** (OS, Python version, GPU, etc.)
* **Include terminal output and error messages**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Provide specific examples to demonstrate the use cases**
* **Describe the current behavior** and explain how the enhancement would improve it
* **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following the coding guidelines below
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Write a clear commit message**
6. **Submit a pull request**

## Development Setup

### Prerequisites

* Python 3.10+
* ffmpeg
* uv package manager

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/fast_simple.git
cd fast_simple

# Install dependencies
./setup.sh

# Run the app
./run.sh
```

### Running Tests

Currently, testing is manual. Run the app and test:
- Recording with F8 hotkey
- Recording with button
- GPU/CPU mode switching
- Text insertion in various applications
- Waveform visualization
- All status transitions

### Project Structure

```
fast_simple/
├── app.py              # Main application code
├── pyproject.toml      # Dependency management
├── setup.sh            # Setup script
├── run.sh              # Run script
├── README.md           # User documentation
├── CONTRIBUTING.md     # This file
└── .github/            # GitHub templates
```

## Coding Guidelines

### Python Style

* Follow [PEP 8](https://pep8.org/) style guide
* Use meaningful variable and function names
* Add docstrings to functions and classes
* Keep functions focused and single-purpose
* Comment complex logic

### Example:

```python
def process_audio(self):
    """Process recorded audio and transcribe to text.

    Handles audio concatenation, WAV file creation, transcription
    via Whisper, punctuation addition, and text insertion.
    """
    if not self.audio_frames:
        self.after(0, lambda: self.status_label.configure(
            text="No audio", text_color="red"
        ))
        return

    # ... rest of implementation
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Good examples:
```
Add support for custom hotkey configuration
Fix GPU detection on Wayland systems
Update README with troubleshooting section
Refactor audio processing for better performance
```

### Branch Naming

* `feature/description` - for new features
* `fix/description` - for bug fixes
* `docs/description` - for documentation
* `refactor/description` - for code refactoring

Examples:
```
feature/custom-hotkeys
fix/wayland-gpu-detection
docs/installation-guide
refactor/audio-pipeline
```

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- [ ] Automated tests (unit tests, integration tests)
- [ ] Custom hotkey configuration UI
- [ ] Multi-language support for transcription
- [ ] macOS and Windows compatibility
- [ ] Performance optimizations

### Medium Priority
- [ ] Alternative STT models (Faster Whisper, etc.)
- [ ] Output text formatting options
- [ ] Audio preprocessing (noise reduction)
- [ ] Configuration file support
- [ ] Keyboard shortcut customization

### Low Priority
- [ ] Themes and UI customization
- [ ] Statistics and usage tracking
- [ ] Export transcription history
- [ ] Voice commands for app control
- [ ] Plugin system

## Documentation

When adding new features:

1. **Update README.md** with usage instructions
2. **Add inline comments** for complex logic
3. **Update troubleshooting section** if applicable
4. **Add configuration examples** if introducing new settings

## Testing Your Changes

Before submitting a PR, please test:

### Functionality Tests
- [ ] Recording works via F8 hotkey
- [ ] Recording works via button
- [ ] Transcription completes successfully
- [ ] Text insertion works in multiple apps
- [ ] GPU mode works (if available)
- [ ] CPU mode works
- [ ] Waveform displays correctly
- [ ] Status updates are accurate

### Environment Tests
- [ ] Works on X11
- [ ] Works on Wayland
- [ ] Works with different desktop environments
- [ ] Fresh install works (`./setup.sh` on clean system)

### Edge Cases
- [ ] No audio recorded
- [ ] Very short recordings
- [ ] Very long recordings
- [ ] No microphone available
- [ ] No GPU available

## Questions?

Feel free to open an issue with the `question` label if you have any questions about contributing.

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for your contribution! 🎉
