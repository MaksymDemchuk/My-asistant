from speak_engine import SpeakEngine
from speech_recognition import Microphone, Recognizer, UnknownValueError, RequestError
from fuzzywuzzy import fuzz

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import sqlite3
import webbrowser as wb
import json
import requests
import datetime
import sys



speak = SpeakEngine("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\TokenEnums\\RHVoice\\Volodymyr")

ALIAS = [
    "ромчік", "рома", "роман", "ромич"
]

LIST_OF_WORDS = [
    "кажи", "шо"
]


class VoiceAssistant:

    def __init__(self):
        self.recognized_voice = None
        self.__recognized = ""
        self.micro = Microphone()
        self.rec = Recognizer()
        self.audio: Recognizer = self.rec

    def call_assistant(self, instance):
        with self.micro as source:
            print("start listening...")
            self.rec.adjust_for_ambient_noise(source)
            self.audio = self.rec.listen(source, phrase_time_limit=4)
            print("End listening!")

            try:
                self.__recognized = self.rec.recognize_google(self.audio, language="uk-UK").lower()
                print(self.__recognized)

            except UnknownValueError:
                self.__recognized = "голос не розпізнано!"

            except RequestError:
                self.__recognized = "RequestError"
            finally:
                self.recognize_command()

    def filtering(self):
        """Для обробки помилкок, фільтрації текстку та ігнорування імені голосового помічника"""
        print("[log] filtering has been called")
        if self.__recognized == "голос не розпізнано!":
            speak("Я вас не почув")
            return 0

        if self.__recognized == "RequestError":
            speak("Немає з'єднання")
            return 0

        words = self.__recognized.split()

        for elem in words:
            if elem in LIST_OF_WORDS:
                self.__recognized = self.__recognized.replace(elem, "")
            if elem in ALIAS:
                self.__recognized = self.__recognized.replace(elem, "")

        if self.__recognized.startswith(" "):
            del self.__recognized[0]
        if self.__recognized.endswith(" "):
            del self.__recognized[-1]

        return self.__recognized

    def recognize_command(self):

        sql = sqlite3.connect("commands.db")
        self.recognized_voice = self.filtering()
        similarity = 80
        for cmd in sql.execute("SELECT * FROM questions"):
            if fuzz.ratio(cmd[0], self.recognized_voice) > similarity:  # cmd[0] - question, cmd[1] - answer
                print("[log]", self.recognized_voice)
                speak(cmd[1])
                sql.close()
                return 0

        for cmd in sql.execute("SELECT * FROM URL"):
            if fuzz.ratio(cmd[0], self.recognized_voice) > similarity:  # cmd[0] - text, cmd[1] - url
                print("[log]", self.recognized_voice)
                wb.open(cmd[1])
                sql.close()
                return 0

        for cmd in sql.execute("SELECT * FROM execute_cmd"):
            if fuzz.ratio(cmd[0], self.recognized_voice) > similarity:  # cmd[0] - request, cmd[1] - calling
                print("[log]", self.recognized_voice)
                FUNCTIONS = {
                    "get_dolar": Function().get_dolar,
                    "now_time": Function().now_time,
                    "get_schedule": Function().get_schedule,
                    "exit": Function()._exit
                }
                for key, value in FUNCTIONS.items():
                    if cmd[1] == key:
                        speak(value())
                        sql.close()
                        break
                return 0

    @staticmethod
    def volume_plus(_):
        speak.volume += 0.1
        print(speak.volume)
        speak("Добре")

    @staticmethod
    def volume_minus(_):
        speak.volume -= 0.1
        print(speak.volume)
        speak("Добре")


class Function:

    
    @staticmethod
    def get_schedule() -> str:
        """
        Тут імпортується модуль в якому виконується запит для розкладу в з якого повертається
        json з якого дістаються та записуються значення дисциплін в змінну disciplins та повертається
        для відтворення аситентом на сьогоднішній день
        """
        import get_subjects
        schedule_data = get_subjects.get_schedule()
        disciplins = ""
        for item in schedule_data['d']:
            if item['full_date'] == get_subjects.get_date(7):
                disciplins += item['study_time'] + " " + item['discipline'] + " "
        
        if disciplins == "":
            return "Сьогодні пари відсутні" # Якщо пари відсутні тоді disciplins буде порожньою і виконається дана умова
        else:
            return "Сьогодні" +disciplins

    @staticmethod
    def now_time() -> str:
        return f"Зараз {datetime.datetime.now().hour}:{datetime.datetime.now().minute}"

    @staticmethod
    def get_dolar() -> str:
        content = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5").content
        data = json.loads(content)
        for elem in data:
            if elem["ccy"] == "USD":
                price = elem["buy"]
                price = price.split(".")
                print(f"зараз по {price[0]} гривень {price[1][:2]} копійок")
                return f"зараз по {price[0]} гривень {price[1][:2]} копійок"

    @staticmethod
    def _exit():
        speak("Бувайте")
        sys.exit()


VA = VoiceAssistant()


class WindowAssistantApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bl = BoxLayout(orientation="vertical", padding=20)
        self.gl = GridLayout(cols=3, spacing=3)

        self.labels = [Label(text="", halign="left", valign="bottom", text_size=(400 - 40, 15),
                       size_hint=(1, .3), font_size=16) for _ in range(10)]

        self.b1 = Button(text="V-",
                         on_press=VA.volume_minus,
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4),
                         font_size=46)
        self.b2 = Button(on_press=VA.call_assistant,
                         background_normal="images/microphone.jpg",
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4))
        self.b3 = Button(text="V+",
                         on_press=VA.volume_plus,
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4),
                         font_size=46)

    def set_label_text(self, text, halign="left"):

        self.labels[-1].text, self.labels[-1].halign = text, halign

    def build(self):

        self.title = "Roma Assistant"

        for elem in self.labels:
            self.bl.add_widget(elem)

        self.gl.add_widget(self.b1)
        self.gl.add_widget(self.b2)
        self.gl.add_widget(self.b3)

        self.bl.add_widget(self.gl)

        return self.bl


if __name__ == '__main__':
    MyApp = WindowAssistantApp()
    MyApp.run()
