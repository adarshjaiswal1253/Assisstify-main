import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import datetime, re, math, random, threading, requests, time, webbrowser, os
from textblob import TextBlob
from collections import defaultdict
from nltk import bigrams
import pyttsx3, speech_recognition as sr
import wikipedia
from bs4 import BeautifulSoup
import json
from urllib.parse import quote_plus

# ---------- AI PDF Summarization ----------
from PyPDF2 import PdfReader
from transformers import pipeline

# ---------- Appearance ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------- Safe evaluator ----------
def safe_eval(expr):
    if not re.match(r"^[\d+\-*/().\s]+$", expr):
        return None
    try:
        result = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "pow": pow})
        return result
    except Exception:
        return None

# ---------- Memory & Data ----------
memory = {}
todo_list = []

training_data = [
    "hello how are you",
    "i am fine thank you",
    "what is your name",
    "my name is chatbot",
    "i can help you with math",
    "today is a beautiful day",
    "goodbye see you later",
    "i like learning new things"
]

bigram_model = defaultdict(list)
for sentence in training_data:
    words = sentence.lower().split()
    for w1, w2 in bigrams(words, pad_right=True, pad_left=True):
        bigram_model[w1].append(w2)

def generate_ngram_reply(start_word="hello", num_words=6):
    word = start_word
    reply = [word]
    for _ in range(num_words):
        if word in bigram_model:
            word = random.choice(bigram_model[word])
            if word is None:
                break
            reply.append(word)
        else:
            break
    return " ".join(reply)

# ---------- Chatbot logic ----------
def chatbot_response(user_input):
    text = user_input.lower().strip()
    tokens = text.split()

    # To-Do List
    if "add" in tokens and "task" in tokens:
        task = text.replace("add task", "").strip()
        if task:
            todo_list.append(task)
            return f"Task added: '{task}' ✅"
        else:
            return "Please specify a task to add."

    if "show" in tokens and "tasks" in tokens:
        if todo_list:
            tasks = "\n".join([f"{i+1}. {t}" for i, t in enumerate(todo_list)])
            return f"📝 Your To-Do List:\n{tasks}"
        else:
            return "Your To-Do List is empty."

    if "delete" in tokens and "task" in tokens:
        match = re.search(r"delete task (\d+)", text)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(todo_list):
                removed = todo_list.pop(idx)
                return f"Deleted task: '{removed}' ❌"
            else:
                return "Task number not found."
        else:
            return "Specify the task number to delete. (e.g. delete task 2)"

    # Date & Time
    if "time" in tokens or "date" in tokens:
        now = datetime.datetime.now()
        return f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    # Sentiment
    sentiment = TextBlob(user_input).sentiment.polarity
    if sentiment > 0.2:
        return "That sounds positive! 😃"
    elif sentiment < -0.2:
        return "I'm sorry to hear that. Stay strong! 🌸"
    else:
        sentiment_reply = "I see! Tell me more."

    # Memory (name)
    match = re.search(r"my name is (.+)", text)
    if match:
        name = match.group(1).strip().title()
        memory["name"] = name
        return f"Nice to meet you, {name}! I'll remember your name."

    if "what" in tokens and "name" in tokens:
        if "name" in memory:
            return f"Your name is {memory['name']}!"
        else:
            return "I don't know your name yet. Tell me by saying 'My name is ...'."

    # Calculator
    expr = text.replace("plus", "+").replace("add", "+")
    expr = expr.replace("minus", "-").replace("subtract", "-")
    expr = expr.replace("times", "*").replace("multiply", "*").replace("x", "*")
    expr = expr.replace("divide", "/").replace("divided by", "/")
    expr = expr.replace("power", "**").replace("^", "**")

    if any(op in expr for op in ["+", "-", "*", "/", "(", ")", "**"]):
        try:
            result = safe_eval(expr)
            if result is not None:
                return f"The answer is {result}"
        except Exception:
            return "Sorry, I couldn't calculate that."

    # Normal chat
    if any(word in tokens for word in ["hello", "hi"]):
        return "Hello! How are you today?"
    if "how" in tokens and "you" in tokens:
        return "I'm just a bot, but I'm doing great! 🤖"
    if "bye" in tokens:
        return "Goodbye! Have a wonderful day!"

    # Fallback ngram
    if tokens:
        return generate_ngram_reply(tokens[0])
    else:
        return sentiment_reply

# ---------- Advanced AI PDF Summarization ----------
ai_summarizer = None
def get_summarizer():
    global ai_summarizer
    if ai_summarizer is None:
        ai_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return ai_summarizer

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text

def advanced_ai_pdf_summarize(pdf_path, chunk_size=1000, max_length=130, min_length=40):
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return "❌ Could not extract text from the PDF."
    # Split into chunks, model limit is 1024 tokens (about 1000 chars is safe)
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summarizer = get_summarizer()
    summary = ""
    for idx, chunk in enumerate(chunks):
        chunk = " ".join(chunk.split())
        if len(chunk) < 60:
            continue
        out = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        sub_summary = out[0]['summary_text']
        summary += f"Part {idx+1}:\n{sub_summary}\n\n"
        if idx >= 4:
            summary += "(Summary truncated... PDF is very long)\n"
            break
    return summary.strip()

def open_and_summarize_pdf_ai():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")], title="Select a PDF to Summarize"
    )
    if not file_path:
        return
    append_chat(f"📄 Summarizing PDF with AI: {os.path.basename(file_path)}", "bot")
    def run_summarize():
        try:
            append_chat("🤖 Loading model and processing PDF, please wait...", "bot")
            summary = advanced_ai_pdf_summarize(file_path)
            append_chat("🤖 AI PDF Summary:", "bot")
            append_chat(summary, "bot")
            speak(summary)
        except Exception as e:
            append_chat(f"❌ AI PDF Summarization error: {e}", "bot")
    threading.Thread(target=run_summarize, daemon=True).start()

# ---------- Voice ----------
voice_enabled = True

def speak(text):
    if voice_enabled:
        def run_speech():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 170)
                engine.setProperty("volume", 1.0)
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=run_speech, daemon=True).start()

def toggle_voice():
    global voice_enabled
    voice_enabled = not voice_enabled
    if voice_enabled:
        voice_btn.configure(text="🔊 Voice: ON", fg_color="#10b981")
    else:
        voice_btn.configure(text="🔇 Voice: OFF", fg_color="#3b3b3b")

def listen_voice():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            append_chat("🎙 Listening...", "bot")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
        command = recognizer.recognize_google(audio)
        append_chat(f"You (voice): {command}", "user")
        threading.Thread(target=search_thread, args=(command,), daemon=True).start()
    except sr.UnknownValueError:
        append_chat("Bot: Sorry, I couldn't understand that.", "bot")
    except Exception as e:
        append_chat(f"Bot: Error: {e}", "bot")

# ---------- UI Helpers ----------
def append_chat(text, tag="bot"):
    chat_box.configure(state="normal")
    chat_box.insert("end", text + "\n\n", tag)
    chat_box.see("end")
    chat_box.configure(state="disabled")

link_counter = 0
def insert_link(text, url):
    global link_counter
    tag_name = f"link{link_counter}"
    link_counter += 1
    chat_box.configure(state="normal")
    start_index = chat_box.index("end-1c")
    chat_box.insert("end", text + "\n", ("link", tag_name))
    end_index = chat_box.index("end-1c")
    chat_box.tag_add(tag_name, start_index, end_index)
    chat_box.tag_config(tag_name, underline=True)
    chat_box.tag_bind(tag_name, "<Button-1>", lambda e, link=url: webbrowser.open(link))
    chat_box.configure(state="disabled")
    chat_box.see("end")

def on_send(event=None):
    user_msg = message_entry.get().strip()
    if not user_msg:
        return
    append_chat(f"You: {user_msg}", "user")
    message_entry.delete(0, "end")
    bot_reply = chatbot_response(user_msg)
    append_chat(f"Assistify Bot: {bot_reply}", "bot")
    speak(bot_reply)

def new_chat_action():
    if messagebox.askyesno("New Chat", "Start a new chat?"):
        chat_box.configure(state="normal")
        chat_box.delete("1.0", "end")
        chat_box.configure(state="disabled")

# ---------- IMPROVED Search Functions ----------

def get_wikipedia_summary(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except wikipedia.DisambiguationError as e:
        options = '\n- '.join(e.options[:5])
        return f"❓ Wikipedia ambiguous. Try being more specific. Some options:\n- {options}"
    except wikipedia.PageError:
        return "❌ Wikipedia: No page found."
    except Exception as e:
        return f"❌ Wikipedia error: {e}"

def search_duckduckgo(query, num_results=5):
    """DuckDuckGo search as primary search engine"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('a', class_='result__a', limit=num_results):
                title = result.get_text()
                href = result.get('href')
                if href:
                    results.append({'title': title, 'url': href})
            
            return results if results else None
        return None
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return None

def search_bing(query, num_results=5):
    """Bing search as fallback"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('li', class_='b_algo', limit=num_results):
                title_tag = result.find('h2')
                link_tag = result.find('a')
                
                if title_tag and link_tag:
                    title = title_tag.get_text()
                    url = link_tag.get('href')
                    if url and url.startswith('http'):
                        results.append({'title': title, 'url': url})
            
            return results if results else None
        return None
    except Exception as e:
        print(f"Bing search error: {e}")
        return None

def search_brave(query, num_results=5):
    """Brave search as another alternative"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        url = f"https://search.brave.com/search?q={quote_plus(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Brave uses different HTML structure
            for result in soup.find_all('div', class_='snippet', limit=num_results):
                title_tag = result.find('span', class_='snippet-title')
                link_tag = result.find_parent('a')
                
                if title_tag and link_tag:
                    title = title_tag.get_text()
                    url = link_tag.get('href')
                    if url and url.startswith('http'):
                        results.append({'title': title, 'url': url})
            
            return results if results else None
        return None
    except Exception as e:
        print(f"Brave search error: {e}")
        return None

def get_web_search_results(query, num_results=5):
    """Try multiple search engines until one works"""
    
    # Try DuckDuckGo first
    results = search_duckduckgo(query, num_results)
    if results:
        return results, "DuckDuckGo"
    
    # Fallback to Bing
    results = search_bing(query, num_results)
    if results:
        return results, "Bing"
    
    # Fallback to Brave
    results = search_brave(query, num_results)
    if results:
        return results, "Brave"
    
    return None, None

def search_youtube_improved(query, num=3):
    """Improved YouTube search with better error handling"""
    try:
        # Try youtubesearchpython first
        from youtubesearchpython import VideosSearch
        search = VideosSearch(query, limit=num)
        result = search.result().get("result", [])
        
        if result:
            videos = []
            for v in result:
                videos.append({
                    'title': v.get("title", "No title"),
                    'url': v.get("link", "")
                })
            return videos
    except Exception as e:
        print(f"YouTube search library error: {e}")
    
    # Fallback to web scraping
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        q = quote_plus(query)
        response = requests.get(f"https://www.youtube.com/results?search_query={q}", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract video IDs using regex
            video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", response.text)
            seen = set()
            unique_ids = [x for x in video_ids if not (x in seen or seen.add(x))]
            
            videos = []
            for vid_id in unique_ids[:num]:
                videos.append({
                    'title': f"Video: {vid_id}",
                    'url': f"https://www.youtube.com/watch?v={vid_id}"
                })
            
            return videos if videos else None
        return None
    except Exception as e:
        print(f"YouTube fallback error: {e}")
        return None

def search_thread(query):
    """Main search function with improved reliability"""
    try:
        append_chat("🔎 Searching the web...", "bot")

        # Wikipedia Search
        try:
            wiki_result = get_wikipedia_summary(query)
            append_chat("📘 Wikipedia summary:", "bot")
            append_chat(wiki_result, "bot")
            speak(wiki_result[:200])  # Speak first 200 chars
        except Exception as e:
            append_chat(f"⚠️ Wikipedia unavailable: {e}", "bot")

        time.sleep(0.5)

        # Web Search (trying multiple engines)
        append_chat("🌐 Web search results:", "bot")
        results, search_engine = get_web_search_results(query, num_results=5)
        
        if results:
            append_chat(f"(Results from {search_engine})", "bot")
            for i, result in enumerate(results):
                title = result.get('title', 'No title')
                url = result.get('url', '')
                if url:
                    insert_link(f"{i+1}. {title}", url)
        else:
            append_chat("⚠️ Web search temporarily unavailable. Try again later.", "bot")
            # Provide a direct Google search link as fallback
            google_url = f"https://www.google.com/search?q={quote_plus(query)}"
            insert_link("🔗 Click here to search on Google", google_url)

        time.sleep(0.5)

        # YouTube Search
        append_chat("🎬 YouTube videos:", "bot")
        videos = search_youtube_improved(query, num=3)
        
        if videos:
            for idx, video in enumerate(videos):
                title = video.get('title', 'No title')
                url = video.get('url', '')
                if url:
                    insert_link(f"{idx+1}. {title}", url)
        else:
            append_chat("⚠️ YouTube search unavailable.", "bot")
            yt_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            insert_link("🔗 Click here to search on YouTube", yt_url)

    except Exception as e:
        append_chat(f"❌ Search error: {e}", "bot")
        # Provide manual search links as ultimate fallback
        append_chat("Here are some direct search links:", "bot")
        insert_link("🔗 Google Search", f"https://www.google.com/search?q={quote_plus(query)}")
        insert_link("🔗 YouTube Search", f"https://www.youtube.com/results?search_query={quote_plus(query)}")

# ---------- Build UI ----------
root = ctk.CTk()
root.title("Assistify")
root.geometry("1200x760")

sidebar = ctk.CTkFrame(root, width=260)
sidebar.pack(side="left", fill="y")

main_area = ctk.CTkFrame(root)
main_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

# Sidebar Top
top_side = ctk.CTkFrame(sidebar)
top_side.pack(fill="x", pady=(12,6), padx=12)

avatar_container = ctk.CTkFrame(top_side, width=48, height=48)
avatar_container.pack(side="left", padx=(0,10))
avatar_container.pack_propagate(False)

bot_img_path = "bot.png"
if os.path.exists(bot_img_path):
    try:
        pil_img = Image.open(bot_img_path).resize((40,40))
        avatar_tk = ImageTk.PhotoImage(pil_img)
        lbl_avatar = ctk.CTkLabel(avatar_container, image=avatar_tk, text="")
        lbl_avatar.image = avatar_tk
        lbl_avatar.pack(expand=True)
    except:
        ctk.CTkLabel(avatar_container, text="🤖", font=("Arial", 20)).pack(expand=True)
else:
    ctk.CTkLabel(avatar_container, text="🤖", font=("Arial", 20)).pack(expand=True)

ctk.CTkLabel(top_side, text="Assistify", font=("Roboto Medium", 18)).pack(side="left")

new_chat_btn = ctk.CTkButton(sidebar, text="＋ New Chat", anchor="w", command=new_chat_action)
new_chat_btn.pack(fill="x", padx=12, pady=(12,4))

ai_pdf_btn = ctk.CTkButton(
    sidebar, text="🤖 AI PDF Summarize", anchor="w", command=open_and_summarize_pdf_ai
)
ai_pdf_btn.pack(fill="x", padx=12)

chat_list_frame = ctk.CTkFrame(sidebar)
chat_list_frame.pack(fill="both", expand=True, padx=12, pady=6)

for i in range(6):
    lbl = ctk.CTkButton(chat_list_frame, text=f"Chat {i+1} — {datetime.datetime.now().strftime('%Y-%m-%d')}",
                       fg_color="#2b2b2b", anchor="w", height=38)
    lbl.pack(fill="x", pady=4)

bottom_info = ctk.CTkFrame(sidebar, fg_color="#101010")
bottom_info.pack(fill="x", padx=12, pady=12)
ctk.CTkLabel(bottom_info, text="Adarsh jaiswal", anchor="w").pack(side="left", padx=8, pady=8)

# --- Main chat area ---
chat_container = ctk.CTkFrame(main_area)
chat_container.pack(fill="both", expand=True)

header = ctk.CTkLabel(chat_container, text="How can I help you?", font=("Roboto Bold", 20))
header.pack(pady=(24,8))

# SCROLLBAR + TEXT
chat_frame = tk.Frame(chat_container, bg="#111214")
chat_frame.pack(fill="both", expand=True, padx=120, pady=(8,12))

chat_box = tk.Text(chat_frame, bg="#111214", fg="#e1e1e1", bd=0, padx=12, pady=12,
                   wrap="word", font=("Arial", 12))
chat_box.configure(state="disabled")
chat_box.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(chat_frame, command=chat_box.yview)
scrollbar.pack(side="right", fill="y")

chat_box.configure(yscrollcommand=scrollbar.set)
chat_box.tag_configure("user", foreground="#7dd3fc", font=("Arial", 12, "bold"))
chat_box.tag_configure("bot", foreground="#c7f9d1", font=("Arial", 12))
chat_box.tag_configure("link", foreground="#8ab4f8", underline=True)

input_frame = ctk.CTkFrame(chat_container, width=950, height=72, corner_radius=18, fg_color="#1b1b1b")
input_frame.pack(pady=(8,24))
input_frame.pack_propagate(False)

left_controls = ctk.CTkFrame(input_frame, fg_color="transparent")
left_controls.pack(side="left", padx=12, pady=8)

search_btn = ctk.CTkButton(left_controls, text="🌐 Search", width=90, height=34,
                           fg_color="#2f3640", corner_radius=10, command=lambda: on_search_click())
search_btn.pack(side="left")

message_entry = ctk.CTkEntry(input_frame, placeholder_text="Message Assistify",
                             width=500, height=42, corner_radius=20)
message_entry.pack(side="left", padx=20)
message_entry.bind("<Return>", on_send)

right_controls = ctk.CTkFrame(input_frame, fg_color="transparent")
right_controls.pack(side="left", padx=6)

send_btn = ctk.CTkButton(right_controls, text="➡", width=48, height=38, corner_radius=10, command=on_send)
send_btn.grid(row=0, column=1)

controls_bar = ctk.CTkFrame(root, height=48)
controls_bar.pack(side="bottom", fill="x", padx=18, pady=10)

voice_btn = ctk.CTkButton(controls_bar, text="🔊 Voice: ON", width=120, command=toggle_voice, fg_color="#10b981")
voice_btn.pack(side="right", padx=8)
listen_button = ctk.CTkButton(controls_bar, text="🎤 Speak", width=120,
                             command=lambda: threading.Thread(target=listen_voice, daemon=True).start(),
                             fg_color="#ef9a9a")
listen_button.pack(side="right")

def on_search_click():
    query = message_entry.get().strip()
    if not query:
        message_entry.focus()
        return
    append_chat(f"You (search): {query}", "user")
    message_entry.delete(0, "end")
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

append_chat("Assistify is ready. Say hi, ask anything or use the Search button for web results!", "bot")

root.mainloop()