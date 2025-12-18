# Assistify - AI-Powered Desktop Assistant

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

A professional, feature-rich desktop AI assistant application built with Python. Assistify combines natural language processing, web search capabilities, voice recognition, and AI-powered PDF summarization into an intuitive GUI.

---

## 📖 Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Module Overview](#module-overview)
- [Development Guide](#development-guide)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### 🤖 Core Functionality
- **Intelligent Chatbot**: Conversational AI with n-gram language model
- **Task Management**: Add, view, and delete to-do list tasks
- **Sentiment Analysis**: Understand emotional context of user input
- **Memory System**: Remember user information (e.g., name)
- **Calculator**: Natural language math expression evaluation

### 🌐 Search Capabilities
- **Wikipedia Integration**: Get summaries and information
- **Multi-Engine Web Search**: DuckDuckGo, Bing, and Brave search with fallback
- **YouTube Search**: Find and link to relevant videos
- **Clickable Results**: Direct links to search results in chat

### 🎤 Voice Features
- **Text-to-Speech**: Listen to bot responses
- **Speech-to-Text**: Speak commands using microphone
- **Voice Toggle**: Enable/disable voice output
- **Voice Feedback**: Audio confirmation of actions

### 📄 Advanced Features
- **AI PDF Summarization**: Summarize PDF documents using transformer models (facebook/bart-large-cnn)
- **Multi-chunk Processing**: Handle large PDFs with intelligent chunking
- **Threading**: Non-blocking operations for responsive UI

## Project Structure

```
assistify/
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration and constants
├── core/
│   ├── __init__.py
│   └── chatbot.py            # Chatbot logic and NLP
├── modules/
│   ├── __init__.py
│   ├── search.py             # Search functionality
│   ├── voice.py              # Voice input/output
│   └── pdf_summarizer.py     # PDF processing and AI summarization
├── ui/
│   ├── __init__.py
│   └── components.py         # UI widgets and components
├── utils/
│   ├── __init__.py
│   └── validators.py         # Utility functions
├── assets/                   # Images and resources
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Microphone for voice features (optional)

### Setup

1. **Clone or download the project**
```bash
cd assistify
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data** (for NLP features)
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## Usage

### Running the Application

```bash
python main.py
```

The application will launch with a modern dark-themed GUI.

### Basic Commands

#### Chatbot
- **Greeting**: "Hello", "Hi"
- **Time**: "What time is it?", "What's today's date?"
- **Tasks**: 
  - "Add task buy groceries"
  - "Show tasks"
  - "Delete task 1"
- **Name Memory**: "My name is John"
- **Math**: "2 + 2", "10 times 5", "sqrt(16)"

#### Search
- Click the **🌐 Search** button or type query and press Enter
- Results from Wikipedia, web, and YouTube appear in chat
- Click links to open in browser

#### Voice
- Click **🎤 Speak** to activate microphone
- Speak your command naturally
- Bot responds with text and audio

#### PDF Summarization
- Click **🤖 AI PDF Summarize** button
- Select a PDF file
- Wait for AI model to process and summarize
- Summary appears in chat

## Configuration

Edit `config/settings.py` to customize:

- **Window size**: `WINDOW_WIDTH`, `WINDOW_HEIGHT`
- **Colors**: All color constants (`COLOR_*`)
- **Fonts**: Font configurations (`FONT_*`)
- **Voice settings**: Speech rate, volume, timeout
- **Search results**: Number of results per engine
- **PDF settings**: Chunk size, max tokens, etc.

## Module Overview

### `config/settings.py`
Centralized configuration for all application settings, colors, fonts, and constants.

### `core/chatbot.py`
- **Chatbot**: Main conversation engine
- **ChatbotMemory**: Persistent user information storage
- **TodoManager**: Task management
- **NGramModel**: Language model for response generation

### `modules/search.py`
- **WikipediaSearch**: Wikipedia integration
- **WebSearch**: Multi-engine search functionality
- **YouTubeSearch**: Video search capabilities
- **SearchManager**: Unified search coordinator

### `modules/voice.py`
- **TextToSpeech**: Voice output using pyttsx3
- **SpeechRecognition**: Voice input using Google Speech API
- **VoiceManager**: Unified voice interface

### `modules/pdf_summarizer.py`
- **PDFProcessor**: Extract text from PDFs
- **AISummarizer**: Hugging Face transformer-based summarization
- **PDFSummarizer**: Unified PDF handling

### `ui/components.py`
- **ChatBox**: Message display widget
- **InputArea**: User input handling
- **ControlBar**: Voice controls
- **Sidebar**: Navigation and options
- **ApplicationWindow**: Main window orchestration

### `utils/validators.py`
- `safe_eval()`: Safe mathematical expression evaluation
- `parse_math_expression()`: Convert natural language to math
- `extract_name_from_input()`: Name extraction
- `extract_task_number()`: Task number extraction

## Dependencies

| Package | Purpose |
|---------|---------|
| customtkinter | Modern GUI framework |
| pillow | Image processing |
| textblob | Sentiment analysis |
| nltk | NLP utilities |
| pyttsx3 | Text-to-speech |
| SpeechRecognition | Speech-to-text |
| wikipedia | Wikipedia API |
| beautifulsoup4 | Web scraping |
| requests | HTTP requests |
| PyPDF2 | PDF processing |
| transformers | AI models (summarization) |
| torch | Deep learning framework |
| youtubesearchpython | YouTube search |

## Architecture

### Design Patterns
- **Singleton Pattern**: Model instances (AI summarizer)
- **Manager Pattern**: VoiceManager, SearchManager coordinate multiple services
- **Component Pattern**: Modular UI components
- **Separation of Concerns**: Clear module boundaries

### Threading
- Long-running operations (search, PDF processing, voice) run on separate threads
- Prevents UI freezing
- Daemon threads for background tasks

## Troubleshooting

### PDF Summarization is slow
- First run downloads the transformer model (~1.6GB)
- Subsequent runs use cached model
- Large PDFs take longer to process

### Voice not working
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- Ensure microphone is properly connected

### Search results empty
- Check internet connection
- Search engines may rate-limit; wait a moment and try again
- Use fallback links provided

### Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Python version must be 3.8+

---

## 🔧 Development Guide

### Adding a New Feature

**Example: Adding a calculator mode**

1. Add logic to `core/chatbot.py`:
```python
def _handle_advanced_calculation(self, expr):
    # Your calculation logic here
    pass
```

2. Update `chatbot_response()` to call it
3. Test in chat!

### Adding a New Search Engine

1. Create class in `modules/search.py`:
```python
class GoogleSearch:
    @staticmethod
    def search(query, num_results=5):
        # Implementation
        pass
```

2. Add to `SearchManager`:
```python
def search_google(self, query):
    return GoogleSearch.search(query)
```

### Testing

Create `tests/test_chatbot.py`:
```python
import unittest
from core.chatbot import Chatbot

class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.bot = Chatbot()
    
    def test_greeting(self):
        response = self.bot.get_response("hello")
        self.assertIn("Hello", response)
```

Run tests:
```bash
python -m unittest tests/test_chatbot.py
```

### Debugging

Enable logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Best Practices

1. **Use constants** - Don't hardcode values
2. **Error handling** - Catch exceptions gracefully
3. **Documentation** - Add docstrings to functions
4. **Type hints** - Use Python type annotations
5. **Testing** - Write tests for new features
6. **Separation** - Keep concerns separated

---

## 🏗️ Project Architecture

### Design Patterns Used

- **Manager Pattern**: `SearchManager`, `VoiceManager` coordinate multiple services
- **Singleton Pattern**: Model instances (AI summarizer)
- **Component Pattern**: Modular UI components
- **Separation of Concerns**: Clear module boundaries

### Module Communication

```
main.py (Orchestrator)
    ├── core/chatbot.py (Logic)
    ├── modules/search.py (Web)
    ├── modules/voice.py (Audio)
    ├── modules/pdf_summarizer.py (PDF)
    └── ui/components.py (Interface)
```

Each module is independent. `main.py` coordinates them.

### Threading Model

- Long-running operations (search, PDF processing, voice) run on separate threads
- Prevents UI freezing
- Daemon threads for background tasks

---

## 🐛 Troubleshooting

### PDF Summarization is slow
- First run downloads the transformer model (~1.6GB)
- Subsequent runs use cached model
- Large PDFs take longer to process

### Voice not working
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- Ensure microphone is properly connected

### Search results empty
- Check internet connection
- Search engines may rate-limit; wait a moment and try again
- Use fallback links provided

### Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Python version must be 3.8+

### Application won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Clear cache
rm -r assistify/__pycache__
rm -r config/__pycache__
rm -r core/__pycache__
```

---

## 📚 Project Structure Details

```
assistify/
├── config/
│   ├── __init__.py
│   └── settings.py           # 50+ configuration constants
├── core/
│   ├── __init__.py
│   └── chatbot.py            # NLP, memory, tasks, calculator
├── modules/
│   ├── __init__.py
│   ├── search.py             # Wikipedia, web, YouTube search
│   ├── voice.py              # Text-to-speech, voice recognition
│   └── pdf_summarizer.py     # PDF processing & AI summarization
├── ui/
│   ├── __init__.py
│   └── components.py         # All GUI widgets
├── utils/
│   ├── __init__.py
│   └── validators.py         # Helper functions
├── assets/                   # Images and resources
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
├── .gitignore                # Git configuration
├── LICENSE                   # MIT License
└── __init__.py              # Package marker
```

### File Descriptions

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Application orchestration | ~350 |
| `config/settings.py` | All configuration constants | ~100 |
| `core/chatbot.py` | NLP, memory, tasks, calculator | ~280 |
| `modules/search.py` | Wikipedia, web, YouTube | ~220 |
| `modules/voice.py` | Text-to-speech, voice input | ~100 |
| `modules/pdf_summarizer.py` | PDF processing & AI | ~100 |
| `ui/components.py` | GUI components | ~350 |
| `utils/validators.py` | Helper functions | ~80 |

---

## 🚀 Performance Optimization

- **Lazy Loading**: Models load on first use
- **Caching**: Transformer models cached after first use
- **Threading**: Long operations in background
- **Memory Management**: Clear todo list in new chat

---

## 🔐 Security Practices

- **Safe Evaluation**: Math expressions validated
- **Input Validation**: All user input checked
- **Exception Handling**: Errors caught gracefully
- **Safe Defaults**: Conservative defaults used

---

## 📈 Future Enhancements

- [ ] Chat history persistence
- [ ] Custom response training
- [ ] Multiple AI models
- [ ] Advanced NLP features
- [ ] REST API
- [ ] Database support
- [ ] Plugin system
- [ ] Dark/Light theme toggle

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- New features have docstrings
- Changes are tested
- Project structure is maintained

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Adarsh Jaiswal**
- Project Lead & Developer
- Email: [Your email]
- GitHub: [Your GitHub profile]

---

## 💬 Support

For issues, questions, or suggestions:
1. Check the troubleshooting section above
2. Review module docstrings
3. Create an issue in the repository
4. Check existing issues for similar problems

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| Total Files | 13 Python + docs |
| Lines of Code | ~2000 |
| Number of Classes | 14+ |
| Number of Functions | 50+ |
| Test Coverage Ready | Yes ✅ |
| Production Ready | Yes ✅ |

---

**Assistify v1.0.0** | Built with ❤️ in Python

Last Updated: December 18, 2025
