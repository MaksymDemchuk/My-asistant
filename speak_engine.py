import pyttsx3


class SpeakEngine:
    def __init__(self, voice, volume=0.5):
        self.voice = voice
        self.volume = volume
        self.speak_engine = pyttsx3.init()

    def __str__(self):
        return self.voice.name

    def __call__(self, text):
        self.speak_engine.setProperty("voice", self.voice)
        self.speak_engine.setProperty("volume", self.volume)
        self.speak_engine.say(text)
        self.speak_engine.runAndWait()
        self.speak_engine.stop()

