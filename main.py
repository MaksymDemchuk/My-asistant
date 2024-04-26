from speak_engine import SpeakEngine
import get_subjects
from config import *

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from speech_recognition import Microphone, Recognizer, UnknownValueError, RequestError
from fuzzywuzzy import fuzz
import sqlite3
import webbrowser as wb
import json
import requests
import datetime
import sys


speak = SpeakEngine(VOICE_PATH)


class Assistant:

    def __init__(self):
        self.filtered_voice = None
        self.__recognized = ""
        self.micro = Microphone()
        self.rec = Recognizer()
        self.audio: Recognizer = self.rec

    def on_micro(self):
        with self.micro as source:
            print("start listening...")
            self.rec.adjust_for_ambient_noise(source)
            self.audio = self.rec.listen(source, phrase_time_limit=4)
            print("End listening!")
            return self.audio

    def call_assistant(self, instance):
        self.on_micro()
        try:
            self.__recognized = self.rec.recognize_google(self.audio, language="uk-UK").lower()
            MyApp.set_label_text(self.__recognized)

        except UnknownValueError:
            self.__recognized = UNKNOWN_VALUE_ERROR

        except RequestError:
            self.__recognized = "RequestError"

        finally:
            self.recognize_command()

    def filtering(self):
        print("[log] filtering has been called")
        if self.__recognized == UNKNOWN_VALUE_ERROR:
            speak(UNKNOWN_VALUE_ERROR)
            return 0

        if self.__recognized == "RequestError":
            print("Немає з'єднання")
            return 0

        words = self.__recognized.split()

        for elem in words:
            if elem in IGNORE_WORDS:
                self.__recognized = self.__recognized.replace(elem, "")

        if self.__recognized.startswith(" "):
            del self.__recognized[0]
        if self.__recognized.endswith(" "):
            del self.__recognized[-1]

        return self.__recognized

    def recognize_command(self):

        sql = sqlite3.connect("commands.db")
        self.filtered_voice = self.filtering()
        similarity = 80
        for cmd in sql.execute("SELECT * FROM questions"):
            if fuzz.ratio(cmd[0], self.filtered_voice) > similarity:
                MyApp.set_label_text(cmd[1], "right")
                speak(cmd[1])
                sql.close()
                return 0

        for cmd in sql.execute("SELECT * FROM URL"):
            if fuzz.ratio(cmd[0], self.filtered_voice) > similarity:
                MyApp.set_label_text(cmd[1], "right")
                wb.open(cmd[1])
                sql.close()
                return 0

        for cmd in sql.execute("SELECT * FROM execute_cmd"):
            services = {
                "get_usd": Service().get_usd,
                "now_time": Service().now_time,
                "get_schedule": Service().get_schedule,
                "exit": Service().exit
            }
            if fuzz.ratio(cmd[0], self.filtered_voice) > similarity:
                for key, value in services.items():
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


class Service:
    
    @staticmethod
    def get_schedule() -> str:
        """
        Request to LNTU schedule. Get json with disciplines
        """
        schedule_data = get_subjects.get_schedule()
        if schedule_data == "404":
            return "Сьогодні пари відсутні"

        disciplines = ""
        for item in schedule_data['d']:
            if item['full_date'] == get_subjects.get_date(7):
                disciplines += item['study_time'] + " " + item['discipline'] + " "

        return "Сьогодні" + disciplines

    @staticmethod
    def now_time() -> str:
        return f"Зараз {datetime.datetime.now().hour}:{datetime.datetime.now().minute}"

    @staticmethod
    def get_usd() -> str:
        content = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5").content
        data = json.loads(content)
        for elem in data:
            if elem["ccy"] == "USD":
                price = elem["buy"]
                price = price.split(".")
                return f"зараз по {price[0]} гривень {price[1][:2]} копійок"

    @staticmethod
    def exit():
        speak(EXITING)
        sys.exit()


assistant = Assistant()


class WindowAssistantApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bl = BoxLayout(orientation="vertical", padding=20)
        self.gl = GridLayout(cols=3, spacing=3)

        self.labels = [Label(text="", halign="left", valign="bottom", text_size=(400 - 40, 15),
                             size_hint=(1, .3), font_size=16) for _ in range(10)]

        self.b1 = Button(text="V-",
                         on_press=assistant.volume_minus,
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4),
                         font_size=46)
        self.b2 = Button(on_press=assistant.call_assistant,
                         background_normal="images/microphone.jpg",
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4))
        self.b3 = Button(text="V+",
                         on_press=assistant.volume_plus,
                         border=(10, 10, 10, 10),
                         size_hint=(1, .4),
                         font_size=46)

    def set_label_text(self, text, halign="left"):
        for i in range(len(self.labels) - 1):
            self.labels[i].text, self.labels[i].halign = self.labels[i + 1].text, self.labels[i + 1].halign

        self.labels[-1].text, self.labels[-1].halign = text, halign

    def build(self):
        self.title = APP_TITLE
        self.icon = APP_ICON

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
