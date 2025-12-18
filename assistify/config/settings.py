"""
Configuration and constants for Assistify application.
"""

# Application Settings
APP_NAME = "Assistify"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Adarsh Jaiswal"

# Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760
WINDOW_TITLE = "Assistify - AI Assistant"

# Appearance
APPEARANCE_MODE = "dark"
COLOR_THEME = "dark-blue"

# Sidebar Settings
SIDEBAR_WIDTH = 260

# Chat Settings
CHAT_MAX_HISTORY = 6
MESSAGE_PADDING_X = 120
MESSAGE_PADDING_Y = 12

# Voice Settings
VOICE_RATE = 170
VOICE_VOLUME = 1.0
VOICE_TIMEOUT = 5
VOICE_PHRASE_TIME_LIMIT = 7

# Search Settings
WEB_SEARCH_RESULTS = 5
YOUTUBE_RESULTS = 3
WIKIPEDIA_SENTENCES = 3

# PDF Settings
PDF_CHUNK_SIZE = 1000
PDF_MAX_LENGTH = 130
PDF_MIN_LENGTH = 40
PDF_MAX_CHUNKS = 5

# Model Settings
PDF_SUMMARIZER_MODEL = "facebook/bart-large-cnn"

# File Paths
BOT_IMAGE_PATH = "bot.png"

# Colors
COLOR_BG_PRIMARY = "#111214"
COLOR_BG_SECONDARY = "#1b1b1b"
COLOR_BG_DARK = "#101010"
COLOR_BG_HOVER = "#2b2b2b"
COLOR_BG_INPUT = "#2f3640"
COLOR_TEXT_PRIMARY = "#e1e1e1"
COLOR_TEXT_USER = "#7dd3fc"
COLOR_TEXT_BOT = "#c7f9d1"
COLOR_LINK = "#8ab4f8"
COLOR_BUTTON_VOICE_ON = "#10b981"
COLOR_BUTTON_VOICE_OFF = "#3b3b3b"
COLOR_BUTTON_VOICE_SPEAK = "#ef9a9a"

# Font Settings
FONT_HEADER = ("Roboto Bold", 20)
FONT_TITLE = ("Roboto Medium", 18)
FONT_CHAT = ("Arial", 12)
FONT_CHAT_BOLD = ("Arial", 12, "bold")

# Training Data
TRAINING_DATA = [
    "hello how are you",
    "i am fine thank you",
    "what is your name",
    "my name is chatbot",
    "i can help you with math",
    "today is a beautiful day",
    "goodbye see you later",
    "i like learning new things"
]

# User Agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
