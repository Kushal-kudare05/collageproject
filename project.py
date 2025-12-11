import sys
import os
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import pyautogui
import tempfile
from gtts import gTTS
from playsound import playsound
from threading import Thread

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# ====== TEXT TO SPEECH USING gTTS ======
def talk(text: str, gui=None):
    if gui:
        gui.append_message(f"Assistant: {text}")
    def _speak():
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "assistant.mp3")
            tts = gTTS(text=text, lang="en", slow=False)  # fast and clear
            tts.save(temp_path)
            playsound(temp_path)
            os.remove(temp_path)
        except Exception as e:
            print("TTS failed:", e)
    Thread(target=_speak).start()  # Non-blocking

# ====== SPEECH TO TEXT ======
def listen(gui=None) -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if gui:
            gui.append_message("🎙 Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="en-in")
        if gui:
            gui.append_message(f"You: {command}")
        return command.lower()
    except Exception:
        talk("Sorry, I didn't hear that.", gui)
        return ""

# ====== ASSISTANT GUI ======
class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Voice Assistant ✨")
        self.setGeometry(300, 100, 700, 550)

        self.setStyleSheet("""
            QWidget {
                background-color: #0a0f24;
                color: #00ffff;
            }
            QTextEdit {
                background-color: #111;
                border: 2px solid #00ffff;
                color: #00ffea;
                font-family: Consolas;
            }
            QLineEdit {
                background-color: #111;
                border: 2px solid #00ffff;
                color: #00ffea;
                font-family: Consolas;
                padding: 6px;
            }
            QPushButton {
                background-color: #00ffff;
                color: #0a0f24;
                font-weight: bold;
                border-radius: 12px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #ff00ff;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("🎤 Personal Assistant")
        self.title.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # Text area
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Type your command here...")
        self.input_field.returnPressed.connect(self.handle_text_input)
        layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()
        self.listen_button = QPushButton("🎙 Speak")
        self.listen_button.clicked.connect(self.voice_command)
        button_layout.addWidget(self.listen_button)

        self.send_button = QPushButton("📨 Send")
        self.send_button.clicked.connect(self.handle_text_input)
        button_layout.addWidget(self.send_button)

        self.exit_button = QPushButton("❌ Exit")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)

        # Greeting
        talk(" Hello, I'm your personal voice assistant. How can I help you?", self)

    def append_message(self, message: str):
        self.text_area.append(message)
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    # ====== VOICE COMMAND ======
    def voice_command(self):
        self.append_message("🎙 Listening... (speak now)")
        Thread(target=self._voice_command_thread).start()

    def _voice_command_thread(self):
        command = listen(self)
        if command:
            self.process_command(command)

    # ====== TEXT INPUT ======
    def handle_text_input(self):
        command = self.input_field.text().strip().lower()
        if command:
            self.append_message(f"You: {command}")
            self.input_field.clear()
            self.process_command(command)

    # ====== PROCESS COMMAND ======
    def process_command(self, command: str):
        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            talk(f"The time is {current_time}", self)

        elif "search wikipedia" in command:
            talk("What should I search?", self)
            topic = listen(self)
            try:
                result = wikipedia.summary(topic, sentences=2)
                talk("According to Wikipedia:", self)
                talk(result, self)
            except Exception:
                talk("I couldn't find anything.", self)

        elif "open youtube" in command:
            talk("Opening YouTube", self)
            webbrowser.open("https://youtube.com")
            


        elif "open google" in command:
            talk("Opening Google", self)
            webbrowser.open("https://google.com")

        elif "brightness up" in command:
            pyautogui.press("brightnessup")
            talk("Increased brightness", self)

        elif "brightness down" in command:
            pyautogui.press("brightnessdown")
            talk("Decreased brightness", self)

        elif "volume up" in command:
            pyautogui.press("volumeup")
            talk("Volume increased", self)

        elif "volume down" in command:
            pyautogui.press("volumedown")
            talk("Volume decreased", self)

        elif "mute" in command:
            pyautogui.press("volumemute")
            talk("Volume muted", self)

        elif "stop" in command or "exit" in command:
            talk("Goodbye!", self)
            self.close()

        else:
            talk("Sorry, I cannot do that yet.", self)

# ====== MAIN ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AssistantGUI()
    gui.show()
    sys.exit(app.exec())
