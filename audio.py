import pygame
from settings import asset_path


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def load_sound(self, name, filename):
        if not self.enabled:
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(asset_path("sfx", filename))
        except (pygame.error, FileNotFoundError):
            print(f"Audio warning: could not load sfx/{filename}")
            self.sounds[name] = None

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if self.enabled and sound is not None:
            sound.play()

    def play_music(self, filename, loops=-1, volume=0.35):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.load(asset_path("music", filename))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except (pygame.error, FileNotFoundError):
            print(f"Audio warning: could not load music/{filename}")

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
