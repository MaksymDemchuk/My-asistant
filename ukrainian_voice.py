# -*- coding: utf-8 -*-

from ukrainian_tts.tts import TTS, Voices, Stress
import pygame
import io
import time


class UkrainianVoice:
    def __init__(self):
        self.tts = TTS(device="cpu")  # can try gpu, mps

    def __call__(self, text):
        pygame.mixer.init()
        self.audio_data = io.BytesIO()
        audio_data, output_text = self.tts.tts(text, Voices.Mykyta.value, Stress.Dictionary.value)
        self.audio_data.write(audio_data.getvalue())
        self.audio_data.seek(0)

        sound = pygame.mixer.Sound(self.audio_data)
        sound.play()

        time.sleep(0.1)
        # Wait until the audio is finished playing
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

        self.audio_data.close()


if __name__ == "__main__":
    speak = UkrainianVoice()
    speak("Привіт. Як в тебе справи?")
    speak("Привіт. Як в тебе діл+а?")
    speak("Привіт. Як в тебе справи?")



