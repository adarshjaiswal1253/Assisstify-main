"""
UI components and widgets for the Assistify application.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import webbrowser
from config.settings import (
    SIDEBAR_WIDTH, MESSAGE_PADDING_X, MESSAGE_PADDING_Y,
    COLOR_BG_PRIMARY, COLOR_BG_SECONDARY, COLOR_BG_DARK, COLOR_BG_HOVER,
    COLOR_BG_INPUT, COLOR_TEXT_PRIMARY, COLOR_TEXT_USER, COLOR_TEXT_BOT,
    COLOR_LINK, COLOR_BUTTON_VOICE_ON, COLOR_BUTTON_VOICE_OFF, COLOR_BUTTON_VOICE_SPEAK,
    FONT_HEADER, FONT_TITLE, FONT_CHAT, FONT_CHAT_BOLD, BOT_IMAGE_PATH, CHAT_MAX_HISTORY
)


class ChatBox:
    """Manages the chat display widget."""
    
    def __init__(self, parent):
        self.chat_frame = tk.Frame(parent, bg=COLOR_BG_PRIMARY)
        self.chat_frame.pack(fill="both", expand=True, padx=MESSAGE_PADDING_X, pady=(MESSAGE_PADDING_Y,12))
        
        self.text_widget = tk.Text(
            self.chat_frame, 
            bg=COLOR_BG_PRIMARY, 
            fg=COLOR_TEXT_PRIMARY, 
            bd=0, 
            padx=12, 
            pady=12,
            wrap="word", 
            font=FONT_CHAT
        )
        self.text_widget.configure(state="disabled")
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.chat_frame, command=self.text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self._configure_tags()
        
        self.link_counter = 0
    
    def _configure_tags(self):
        """Configure text tags for different message types."""
        self.text_widget.tag_configure("user", foreground=COLOR_TEXT_USER, font=FONT_CHAT_BOLD)
        self.text_widget.tag_configure("bot", foreground=COLOR_TEXT_BOT, font=FONT_CHAT)
        self.text_widget.tag_configure("link", foreground=COLOR_LINK, underline=True)
    
    def append_message(self, text, tag="bot"):
        """Append message to chat box."""
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", text + "\n\n", tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
    
    def insert_link(self, text, url):
        """Insert a clickable link."""
        tag_name = f"link{self.link_counter}"
        self.link_counter += 1
        
        self.text_widget.configure(state="normal")
        start_index = self.text_widget.index("end-1c")
        self.text_widget.insert("end", text + "\n", ("link", tag_name))
        end_index = self.text_widget.index("end-1c")
        self.text_widget.tag_add(tag_name, start_index, end_index)
        self.text_widget.tag_config(tag_name, underline=True)
        self.text_widget.tag_bind(tag_name, "<Button-1>", lambda e, link=url: webbrowser.open(link))
        self.text_widget.configure(state="disabled")
        self.text_widget.see("end")
    
    def clear(self):
        """Clear chat box."""
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")


class InputArea:
    """Manages user input area."""
    
    def __init__(self, parent, on_send_callback):
        self.frame = ctk.CTkFrame(parent, width=950, height=72, corner_radius=18, fg_color=COLOR_BG_SECONDARY)
        self.frame.pack(pady=(8, 24))
        self.frame.pack_propagate(False)
        
        # Left controls
        left_controls = ctk.CTkFrame(self.frame, fg_color="transparent")
        left_controls.pack(side="left", padx=12, pady=8)
        
        self.search_btn = ctk.CTkButton(
            left_controls, 
            text="🌐 Search", 
            width=90, 
            height=34,
            fg_color=COLOR_BG_INPUT, 
            corner_radius=10
        )
        self.search_btn.pack(side="left")
        
        # Message entry
        self.entry = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Message Assistify",
            width=500, 
            height=42, 
            corner_radius=20
        )
        self.entry.pack(side="left", padx=20)
        self.entry.bind("<Return>", lambda e: on_send_callback())
        
        # Right controls
        right_controls = ctk.CTkFrame(self.frame, fg_color="transparent")
        right_controls.pack(side="left", padx=6)
        
        self.send_btn = ctk.CTkButton(
            right_controls, 
            text="➡", 
            width=48, 
            height=38, 
            corner_radius=10, 
            command=on_send_callback
        )
        self.send_btn.grid(row=0, column=1)
    
    def get_input(self):
        """Get input text."""
        return self.entry.get().strip()
    
    def clear_input(self):
        """Clear input field."""
        self.entry.delete(0, "end")


class ControlBar:
    """Manages bottom control bar."""
    
    def __init__(self, parent, on_voice_toggle, on_listen):
        self.frame = ctk.CTkFrame(parent, height=48)
        self.frame.pack(side="bottom", fill="x", padx=18, pady=10)
        
        self.voice_btn = ctk.CTkButton(
            self.frame, 
            text="🔊 Voice: ON", 
            width=120, 
            command=on_voice_toggle, 
            fg_color=COLOR_BUTTON_VOICE_ON
        )
        self.voice_btn.pack(side="right", padx=8)
        
        self.listen_btn = ctk.CTkButton(
            self.frame, 
            text="🎤 Speak", 
            width=120,
            command=on_listen,
            fg_color=COLOR_BUTTON_VOICE_SPEAK
        )
        self.listen_btn.pack(side="right")
    
    def update_voice_button(self, enabled):
        """Update voice button state."""
        if enabled:
            self.voice_btn.configure(text="🔊 Voice: ON", fg_color=COLOR_BUTTON_VOICE_ON)
        else:
            self.voice_btn.configure(text="🔇 Voice: OFF", fg_color=COLOR_BUTTON_VOICE_OFF)


class Sidebar:
    """Manages sidebar with navigation and options."""
    
    def __init__(self, parent, on_new_chat, on_pdf_summarize, author_name):
        self.frame = ctk.CTkFrame(parent, width=SIDEBAR_WIDTH)
        self.frame.pack(side="left", fill="y")
        
        # Top section
        top_side = ctk.CTkFrame(self.frame)
        top_side.pack(fill="x", pady=(12, 6), padx=12)
        
        avatar_container = ctk.CTkFrame(top_side, width=48, height=48)
        avatar_container.pack(side="left", padx=(0, 10))
        avatar_container.pack_propagate(False)
        
        if os.path.exists(BOT_IMAGE_PATH):
            try:
                pil_img = Image.open(BOT_IMAGE_PATH).resize((40, 40))
                avatar_tk = ImageTk.PhotoImage(pil_img)
                lbl_avatar = ctk.CTkLabel(avatar_container, image=avatar_tk, text="")
                lbl_avatar.image = avatar_tk
                lbl_avatar.pack(expand=True)
            except:
                ctk.CTkLabel(avatar_container, text="🤖", font=("Arial", 20)).pack(expand=True)
        else:
            ctk.CTkLabel(avatar_container, text="🤖", font=("Arial", 20)).pack(expand=True)
        
        ctk.CTkLabel(top_side, text="Assistify", font=FONT_TITLE).pack(side="left")
        
        # Buttons
        ctk.CTkButton(self.frame, text="＋ New Chat", anchor="w", command=on_new_chat).pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkButton(self.frame, text="🤖 AI PDF Summarize", anchor="w", command=on_pdf_summarize).pack(fill="x", padx=12)
        
        # Chat history
        chat_list_frame = ctk.CTkFrame(self.frame)
        chat_list_frame.pack(fill="both", expand=True, padx=12, pady=6)
        
        for i in range(CHAT_MAX_HISTORY):
            ctk.CTkButton(
                chat_list_frame, 
                text=f"Chat {i+1}",
                fg_color=COLOR_BG_HOVER, 
                anchor="w", 
                height=38
            ).pack(fill="x", pady=4)
        
        # Bottom info
        bottom_info = ctk.CTkFrame(self.frame, fg_color=COLOR_BG_DARK)
        bottom_info.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(bottom_info, text=author_name, anchor="w").pack(side="left", padx=8, pady=8)


class ApplicationWindow:
    """Main application window."""
    
    def __init__(self, app_name, width, height):
        self.root = ctk.CTk()
        self.root.title(app_name)
        self.root.geometry(f"{width}x{height}")
        
        self.chat_box = None
        self.input_area = None
        self.control_bar = None
        self.sidebar = None
    
    def setup_ui(self, on_new_chat, on_pdf_summarize, on_voice_toggle, on_listen, on_send_callback, author_name):
        """Setup all UI components."""
        # Sidebar
        self.sidebar = Sidebar(self.root, on_new_chat, on_pdf_summarize, author_name)
        
        # Main area
        main_area = ctk.CTkFrame(self.root)
        main_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(main_area, text="How can I help you?", font=FONT_HEADER).pack(pady=(24, 8))
        
        # Chat box
        self.chat_box = ChatBox(main_area)
        
        # Input area
        self.input_area = InputArea(main_area, on_send_callback)
        
        # Control bar
        self.control_bar = ControlBar(self.root, on_voice_toggle, on_listen)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
    
    def get_root(self):
        """Get root window reference."""
        return self.root
