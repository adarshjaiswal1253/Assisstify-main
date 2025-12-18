"""
Assistify - AI-powered Desktop Assistant
Main application entry point and orchestration.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import os

from config.settings import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, APPEARANCE_MODE, 
    COLOR_THEME, APP_AUTHOR
)
from core.chatbot import Chatbot
from modules.search import SearchManager
from modules.voice import VoiceManager
from modules.pdf_summarizer import PDFSummarizer
from ui.components import ApplicationWindow


class AssistifyApp:
    """Main Assistify application class."""
    
    def __init__(self):
        # Initialize components
        self.chatbot = Chatbot()
        self.search_manager = SearchManager()
        self.voice_manager = VoiceManager()
        self.pdf_summarizer = PDFSummarizer()
        
        # Setup appearance
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        
        # Create UI
        self.app_window = ApplicationWindow(APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.app_window.setup_ui(
            on_new_chat=self.new_chat_action,
            on_pdf_summarize=self.open_and_summarize_pdf,
            on_voice_toggle=self.toggle_voice,
            on_listen=self.listen_voice,
            on_send_callback=self.send_message,
            author_name=APP_AUTHOR
        )
    
    def send_message(self, event=None):
        """Handle user message sending."""
        user_msg = self.app_window.input_area.get_input()
        if not user_msg:
            return
        
        # Display user message
        self.app_window.chat_box.append_message(f"You: {user_msg}", "user")
        self.app_window.input_area.clear_input()
        
        # Get bot response
        bot_reply = self.chatbot.get_response(user_msg)
        self.app_window.chat_box.append_message(f"Assistify Bot: {bot_reply}", "bot")
        
        # Speak response
        self.voice_manager.speak(bot_reply)
    
    def new_chat_action(self):
        """Handle new chat action."""
        if messagebox.askyesno("New Chat", "Start a new chat?"):
            self.app_window.chat_box.clear()
            self.chatbot.todo.clear_tasks()
    
    def toggle_voice(self):
        """Toggle voice output."""
        enabled = self.voice_manager.toggle_voice()
        self.app_window.control_bar.update_voice_button(enabled)
    
    def listen_voice(self):
        """Listen for voice input, wait before 'no result', and show all search results for voice-triggered search."""
        self.app_window.chat_box.append_message("🎙 Listening... Speak now!", "bot")

        def run_listen():
            try:
                command = self.voice_manager.listen()
                if command and len(command.strip()) > 0:
                    self.app_window.chat_box.append_message(f"You (voice): {command}", "user")
                    # If the command looks like a search, run full search (Wikipedia, web, YouTube)
                    search_keywords = ["search", "find", "look up", "google", "youtube"]
                    if any(kw in command.lower() for kw in search_keywords):
                        self.app_window.chat_box.append_message("🔎 Voice search triggered. Gathering results...", "bot")
                        # Run search in this thread for voice
                        try:
                            # Wikipedia
                            wiki_result = self.search_manager.wikipedia.get_summary(command)
                            self.app_window.chat_box.append_message("📘 Wikipedia summary:", "bot")
                            self.app_window.chat_box.append_message(wiki_result, "bot")
                            self.voice_manager.speak(wiki_result[:200])
                        except Exception as e:
                            self.app_window.chat_box.append_message(f"⚠️ Wikipedia unavailable: {e}", "bot")

                        # Web Search
                        results, search_engine = self.search_manager.web.get_results(command)
                        if results:
                            self.app_window.chat_box.append_message("🌐 Web search results:\n", "bot")
                            self.app_window.chat_box.append_message(f"(Results from {search_engine})\n", "bot")
                            for i, result in enumerate(results):
                                title = result.get('title', 'No title')
                                url = result.get('url', '')
                                if url:
                                    self.app_window.chat_box.insert_link(f"{i+1}. {title}", url)
                        else:
                            self.app_window.chat_box.append_message("🌐 Web search - No results found.", "bot")

                        # YouTube Search
                        videos = self.search_manager.youtube.search(command)
                        if videos:
                            self.app_window.chat_box.append_message("🎬 YouTube videos:\n", "bot")
                            for idx, video in enumerate(videos):
                                title = video.get('title', 'No title')
                                url = video.get('url', '')
                                if url:
                                    self.app_window.chat_box.insert_link(f"{idx+1}. {title}", url)
                        else:
                            self.app_window.chat_box.append_message("🎬 YouTube - No videos found.", "bot")
                    else:
                        # Not a search, treat as normal chat
                        bot_reply = self.chatbot.get_response(command)
                        self.app_window.chat_box.append_message(f"Assistify Bot: {bot_reply}", "bot")
                        self.voice_manager.speak(bot_reply)
                else:
                    # Wait a few seconds before showing 'no result'
                    time.sleep(2.5)
                    self.app_window.chat_box.append_message("🎙 Sorry, I couldn't understand that. Please try again.", "bot")
            except Exception as e:
                error_msg = f"🎙 Error: {str(e)}"
                print(error_msg)
                self.app_window.chat_box.append_message(error_msg, "bot")

        thread = threading.Thread(target=run_listen, daemon=True)
        thread.start()
    
    def open_and_summarize_pdf(self):
        """Open PDF file and summarize with AI."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")], 
            title="Select a PDF to Summarize"
        )
        if not file_path:
            return
        
        self.app_window.chat_box.append_message(
            f"📄 Summarizing PDF with AI: {os.path.basename(file_path)}", 
            "bot"
        )
        
        def run_summarize():
            try:
                self.app_window.chat_box.append_message(
                    "🤖 Loading model and processing PDF, please wait...", 
                    "bot"
                )
                summary = self.pdf_summarizer.summarize_file(file_path)
                self.app_window.chat_box.append_message("🤖 AI PDF Summary:", "bot")
                self.app_window.chat_box.append_message(summary, "bot")
                self.voice_manager.speak(summary[:200])
            except Exception as e:
                self.app_window.chat_box.append_message(f"❌ PDF Summarization error: {e}", "bot")
        
        threading.Thread(target=run_summarize, daemon=True).start()
    
    def search_thread(self, query):
        """Perform comprehensive search."""
        try:
            self.app_window.chat_box.append_message("🔎 Searching the web...", "bot")
            
            # Wikipedia Search
            try:
                wiki_result = self.search_manager.wikipedia.get_summary(query)
                self.app_window.chat_box.append_message("📘 Wikipedia summary:", "bot")
                self.app_window.chat_box.append_message(wiki_result, "bot")
                self.voice_manager.speak(wiki_result[:200])
            except Exception as e:
                self.app_window.chat_box.append_message(f"⚠️ Wikipedia unavailable: {e}", "bot")
            
            time.sleep(0.5)
            
            # Web Search
            results, search_engine = self.search_manager.web.get_results(query)
            
            if results:
                self.app_window.chat_box.append_message("🌐 Web search results:\n", "bot")
                self.app_window.chat_box.append_message(f"(Results from {search_engine})\n", "bot")
                for i, result in enumerate(results):
                    title = result.get('title', 'No title')
                    url = result.get('url', '')
                    if url:
                        self.app_window.chat_box.insert_link(f"{i+1}. {title}", url)
            else:
                self.app_window.chat_box.append_message("🌐 Web search - No results found.", "bot")
            
            time.sleep(0.5)
            
            # YouTube Search
            videos = self.search_manager.youtube.search(query)
            
            if videos:
                self.app_window.chat_box.append_message("🎬 YouTube videos:\n", "bot")
                for idx, video in enumerate(videos):
                    title = video.get('title', 'No title')
                    url = video.get('url', '')
                    if url:
                        self.app_window.chat_box.insert_link(f"{idx+1}. {title}", url)
            else:
                self.app_window.chat_box.append_message("🎬 YouTube - No videos found.", "bot")
        
        except Exception as e:
            self.app_window.chat_box.append_message(f"❌ Search error: {e}", "bot")
    
    def on_search_click(self):
        """Handle search button click."""
        query = self.app_window.input_area.get_input()
        if not query:
            self.app_window.input_area.entry.focus()
            return
        
        self.app_window.chat_box.append_message(f"You (search): {query}", "user")
        self.app_window.input_area.clear_input()
        threading.Thread(target=self.search_thread, args=(query,), daemon=True).start()
    
    def run(self):
        """Run the application."""
        # Set search button command
        self.app_window.input_area.search_btn.configure(command=self.on_search_click)
        
        # Initial greeting
        self.app_window.chat_box.append_message(
            "Assistify is ready. Say hi, ask anything or use the Search button for web results!", 
            "bot"
        )
        
        # Start application
        self.app_window.run()


def main():
    """Entry point for the application."""
    app = AssistifyApp()
    app.run()


if __name__ == "__main__":
    main()
