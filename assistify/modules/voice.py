"""
Voice input and output functionality - Simplified and Fixed.
"""

import pyttsx3
import speech_recognition as sr
import threading
from config.settings import VOICE_RATE, VOICE_VOLUME, VOICE_TIMEOUT, VOICE_PHRASE_TIME_LIMIT


class TextToSpeech:
    """Handles text-to-speech conversion."""
    
    def __init__(self):
        self.enabled = True
    
    def speak(self, text):
        """
        Convert text to speech.
        
        Args:
            text (str): Text to speak
        """
        if self.enabled and text and len(text.strip()) > 0:
            def run_speech():
                try:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", VOICE_RATE)
                    engine.setProperty("volume", VOICE_VOLUME)
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"❌ Text-to-speech error: {e}")
            
            thread = threading.Thread(target=run_speech, daemon=True)
            thread.start()
    
    def toggle(self):
        """Toggle voice on/off."""
        self.enabled = not self.enabled
        return self.enabled
    
    def is_enabled(self):
        """Check if voice is enabled."""
        return self.enabled


class SpeechRecognition:
    """Handles speech-to-text conversion - Simple and Reliable."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
    
    def listen(self, timeout=VOICE_TIMEOUT, phrase_time_limit=VOICE_PHRASE_TIME_LIMIT):
        """
        Listen to microphone and convert to text.
        
        Args:
            timeout (int): Timeout in seconds
            phrase_time_limit (int): Phrase time limit in seconds
            
        Returns:
            str or None: Recognized text or None if failed
        """
        try:
            with sr.Microphone() as source:
                print("🎙 Listening... Speak now!")
                
                # Listen with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech using Google API
            print("🎙 Processing...")
            command = self.recognizer.recognize_google(audio, language='en-US')
            print(f"✅ You said: {command}")
            return command
            
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("❌ No speech detected")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None




class VoiceManager:
    """Unified voice manager for both input and output."""
    
    def __init__(self):
        self.tts = TextToSpeech()
        self.stt = SpeechRecognition()
        self.is_listening = False
    
    def speak(self, text):
        """Speak text."""
        if text and len(text.strip()) > 0:
            self.tts.speak(text)
    
    def listen(self):
        """Listen to user."""
        if self.is_listening:
            return None
        
        self.is_listening = True
        try:
            command = self.stt.listen()
            return command
        finally:
            self.is_listening = False
    
    def toggle_voice(self):
        """Toggle voice output."""
        return self.tts.toggle()
    
    def is_voice_enabled(self):
        """Check if voice is enabled."""
        return self.tts.is_enabled()
