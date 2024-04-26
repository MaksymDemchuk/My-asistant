import sqlite3
import sys

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.textinput import TextInput

# from kivy.config import Config

db = sqlite3.connect('commands.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS questions (
command TEXT,
answer TEXT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS URL (
command TEXT,
url TEXT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS execute_cmd (
command TEXT,
link TEXT
)""")


db.commit()


def add_cmd(instance):
    print(instance.text)
    cmd = myApp.text_cmd.text
    answer = myApp.text_response.text
    sql.execute("INSERT INTO " + instance.text + " VALUES (?,?)", (cmd, answer))
    db.commit()
    myApp.lbl.text = f"Додано команду: {myApp.text_cmd.text}"
    myApp.text_cmd.text = ""
    myApp.text_response.text = ""


def print_all():
    print("===================ALL_COMMANDS===================")
    for elem in sql.execute("SELECT * FROM questions"):
        print(elem[0] + (" " * (35 - len(elem[0]))) + "| " + elem[1])
    print("======================URLS========================")
    for elem in sql.execute("SELECT * FROM URL"):
        print(elem[0] + (" " * (35 - len(elem[0]))) + "| " + elem[1])
    print("====================EXEC_CMDS=====================")
    for elem in sql.execute("SELECT * FROM execute_cmd"):
        print(elem[0] + (" " * (35 - len(elem[0]))) + "| " + elem[1])
    print("==================================================")


def delete():
    table = input("Select a table: ")
    elem = input("Select a question: ")
    sql.execute(f"DELETE from {table} where command = '{elem}'")
    print("The questions has been deleted!")
    db.commit()

def exit():
    sys.exit()


class AddCommandApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bl = BoxLayout(orientation="vertical", padding=20)
        self.gl = GridLayout(cols=3, spacing=3)

        self.text_cmd = TextInput(size_hint=(1, .5))
        self.text_response = TextInput(size_hint=(1, .5))

        self.lbl_cmd = Label(text="Команда", font_size=20, halign="left", valign="center", size_hint=(1, .5),
                             text_size=(Window.size[0] - 40, Window.size[1] / 20))

        self.lbl_responce = Label(text="Відповідь",
                                  font_size=20,
                                  halign="left",
                                  valign="center",
                                  size_hint=(1, .5),
                                  text_size=(Window.size[0] - 40, Window.size[1] / 20))

        self.lbl = Label(text="Добавте команду",
                         font_size=20,
                         halign="left",
                         valign="center",
                         size_hint=(1, .5),
                         text_size=(Window.size[0] - 40, Window.size[1] / 20))

        self.lbl1 = Label(text="Виберіть таблицю:",
                          font_size=20,
                          halign="left",
                          valign="center",
                          size_hint=(1, .5),
                          text_size=(Window.size[0] - 40, Window.size[1] / 20))

    def build(self):
        self.bl.add_widget(self.lbl_cmd)
        self.bl.add_widget(self.text_cmd)
        self.bl.add_widget(self.lbl_responce)
        self.bl.add_widget(self.text_response)
        self.bl.add_widget(self.lbl)
        self.bl.add_widget(self.lbl1)
        self.gl.add_widget(Button(text="Questions", on_press=add_cmd, font_size=32))
        self.gl.add_widget(Button(text="URL", on_press=add_cmd, font_size=32))
        self.gl.add_widget(Button(text="execute_cmd", on_press=add_cmd, font_size=32))

        self.bl.add_widget(self.gl)
        return self.bl


if __name__ == "__main__":
    myApp = AddCommandApp()
    myApp.run()
