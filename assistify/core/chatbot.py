"""
Core chatbot logic and NLP processing.
"""

from textblob import TextBlob
from collections import defaultdict
from nltk import bigrams
import random
import re
from utils.validators import safe_eval, parse_math_expression, extract_name_from_input, extract_task_number
from config.settings import TRAINING_DATA


class ChatbotMemory:
    """Manages chatbot memory and user information."""
    
    def __init__(self):
        self.data = {}
    
    def set(self, key, value):
        """Store information."""
        self.data[key] = value
    
    def get(self, key, default=None):
        """Retrieve stored information."""
        return self.data.get(key, default)
    
    def clear(self):
        """Clear all memory."""
        self.data.clear()


class TodoManager:
    """Manages to-do list tasks."""
    
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task):
        """Add a new task."""
        if task:
            self.tasks.append(task)
            return True
        return False
    
    def remove_task(self, index):
        """Remove task by index (0-based)."""
        if 0 <= index < len(self.tasks):
            return self.tasks.pop(index)
        return None
    
    def get_all_tasks(self):
        """Get all tasks."""
        return self.tasks
    
    def clear_tasks(self):
        """Clear all tasks."""
        self.tasks.clear()


class NGramModel:
    """N-Gram language model for response generation."""
    
    def __init__(self, training_data):
        self.model = defaultdict(list)
        self._train(training_data)
    
    def _train(self, training_data):
        """Train the n-gram model."""
        for sentence in training_data:
            words = sentence.lower().split()
            for w1, w2 in bigrams(words, pad_right=True, pad_left=True):
                self.model[w1].append(w2)
    
    def generate_reply(self, start_word="hello", num_words=6):
        """Generate a response using n-gram model."""
        word = start_word
        reply = [word]
        for _ in range(num_words):
            if word in self.model:
                word = random.choice(self.model[word])
                if word is None:
                    break
                reply.append(word)
            else:
                break
        return " ".join(reply)


class Chatbot:
    """Main chatbot class handling conversational logic."""
    
    def __init__(self):
        self.memory = ChatbotMemory()
        self.todo = TodoManager()
        self.ngram = NGramModel(TRAINING_DATA)
    
    def get_response(self, user_input):
        """
        Process user input and generate response.
        
        Args:
            user_input (str): User's message
            
        Returns:
            str: Bot's response
        """
        text = user_input.lower().strip()
        tokens = text.split()
        
        # To-Do List Management
        if "add" in tokens and "task" in tokens:
            return self._handle_add_task(text)
        
        if "show" in tokens and "tasks" in tokens:
            return self._handle_show_tasks()
        
        if "delete" in tokens and "task" in tokens:
            return self._handle_delete_task(text)
        
        # Date & Time
        if "time" in tokens or "date" in tokens:
            return self._handle_time_request()
        
        # Memory (name)
        name_input = extract_name_from_input(text)
        if name_input:
            self.memory.set("name", name_input)
            return f"Nice to meet you, {name_input}! I'll remember your name."
        
        if "what" in tokens and "name" in tokens:
            return self._handle_name_query()
        
        # Calculator
        expr = parse_math_expression(text)
        if any(op in expr for op in ["+", "-", "*", "/", "(", ")", "**"]):
            return self._handle_calculation(expr)
        
        # Sentiment & Normal Chat
        return self._handle_sentiment_and_chat(user_input, tokens)
    
    def _handle_add_task(self, text):
        """Handle adding a task."""
        task = text.replace("add task", "").strip()
        if self.todo.add_task(task):
            return f"Task added: '{task}' ✅"
        else:
            return "Please specify a task to add."
    
    def _handle_show_tasks(self):
        """Handle showing tasks."""
        tasks = self.todo.get_all_tasks()
        if tasks:
            task_list = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])
            return f"📝 Your To-Do List:\n{task_list}"
        else:
            return "Your To-Do List is empty."
    
    def _handle_delete_task(self, text):
        """Handle deleting a task."""
        task_num = extract_task_number(text)
        if task_num:
            removed = self.todo.remove_task(task_num - 1)
            if removed:
                return f"Deleted task: '{removed}' ❌"
            else:
                return "Task number not found."
        else:
            return "Specify the task number to delete. (e.g. delete task 2)"
    
    def _handle_time_request(self):
        """Handle time/date requests."""
        import datetime
        now = datetime.datetime.now()
        return f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _handle_name_query(self):
        """Handle name queries."""
        name = self.memory.get("name")
        if name:
            return f"Your name is {name}!"
        else:
            return "I don't know your name yet. Tell me by saying 'My name is ...'."
    
    def _handle_calculation(self, expr):
        """Handle mathematical calculations."""
        result = safe_eval(expr)
        if result is not None:
            return f"The answer is {result}"
        else:
            return "Sorry, I couldn't calculate that."
    
    def _handle_sentiment_and_chat(self, user_input, tokens):
        """Handle sentiment analysis and normal conversation."""
        sentiment = TextBlob(user_input).sentiment.polarity
        
        if sentiment > 0.2:
            return "That sounds positive! 😃"
        elif sentiment < -0.2:
            return "I'm sorry to hear that. Stay strong! 🌸"
        
        # Normal chat
        if any(word in tokens for word in ["hello", "hi"]):
            return "Hello! How are you today?"
        if "how" in tokens and "you" in tokens:
            return "I'm just a bot, but I'm doing great! 🤖"
        if "bye" in tokens:
            return "Goodbye! Have a wonderful day!"
        
        # Fallback ngram
        if tokens:
            return self.ngram.generate_reply(tokens[0])
        else:
            return "I see! Tell me more."
