import sys
import os
import numpy as np
import librosa
import threading
import pygame
from PIL import Image
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play
import time

class RealTimeLipSyncUI:
    def __init__(self,open_img_path, closed_img_path, screen_size=(800, 800), fps=24, threshold=0.2,face = False):
        pygame.init()
        self.screen_size = screen_size
        self.image_size = (400, 575)  # Küçük resim boyutu
        self.fps = fps
        self.threshold = threshold
        self.queue = []
        self.closed = False
        self.clock = pygame.time.Clock()
        self.current_audio_thread = None
        self.mouth_states = []
        self.current_frame_index = 0
        self.audio_playing = False
        self.subtitle_text = ""
        self.space = False
        self.face = face
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("BotFace")

        self.open_img = pygame.image.load(open_img_path).convert_alpha()
        self.closed_img = pygame.image.load(closed_img_path).convert_alpha()

        self.background_color = (30, 30, 60)  # Arka plan rengi
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        self.screen.fill(self.background_color)

        self.draw_image_centered(self.closed_img)

        # Altyazı fontu

    def analyze_audio(self, audio_file):
        y, sr = librosa.load(audio_file, sr=None)
        frame_duration = 1.0 / self.fps
        frame_length = int(sr * frame_duration)

        energy = np.array([
            np.sum(np.abs(y[i:i + frame_length] ** 2))
            for i in range(0, len(y), frame_length)
        ])

        energy_norm = (energy - energy.min()) / (energy.max() - energy.min() + 1e-6)
        mouth_states = ['open' if e > self.threshold else 'closed' for e in energy_norm]
        return mouth_states
    
    def draw_image_centered(self, img):
        if self.face:
            scaled_img = pygame.transform.scale(img, self.image_size)
            x = (self.screen_size[0] - self.image_size[0]) // 2
            y = (self.screen_size[1] - self.image_size[1]) // 2 - 100
            self.screen.blit(scaled_img, (x, y))

    def play_audio(self, filepath):
        def _play():
            audio = AudioSegment.from_file(filepath, format="wav")
            playback = play(audio)
            playback.wait_done()
        self.current_audio_thread = threading.Thread(target=_play, daemon=True)
        self.current_audio_thread.start()

    def generate_response(self, audio_path, subtitle_text):
        self.queue.append((audio_path, subtitle_text))

    def force_flip(self):
        # Ekranı zorla güncelle, dışarıdan bir scriptte subtitle güncellemesi yapılırken
        self.screen.fill(self.background_color)
        self.draw_image_centered(self.closed_img)
        self.draw_subtitle(self.subtitle_text)
        pygame.display.flip()

    def draw_subtitle(self, text):
        lines = self.wrap_text(text, self.font, self.screen_size[0] - 40)
        y_offset = self.screen_size[1] - len(lines) * 30 - 30
        for i, line in enumerate(lines):
            rendered_text = self.font.render(line, True, (255, 255, 255))
            text_rect = rendered_text.get_rect(center=(self.screen_size[0] // 2, y_offset + i * 30))
            self.screen.blit(rendered_text, text_rect)

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def run(self):
        while not self.closed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_program()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.space = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.space = False
            self.screen.fill(self.background_color)
            
            if not self.audio_playing and self.queue:
                self.audio_playing = True
                audio_path, subtitle = self.queue.pop(0)
                self.subtitle_text = subtitle
                self.mouth_states = self.analyze_audio(audio_path)
                self.current_frame_index = 0
                self.play_audio(audio_path)

            if self.audio_playing and self.mouth_states:

                if self.current_audio_thread and not self.current_audio_thread.is_alive():
                    self.audio_playing = False
                    self.mouth_states = []
                    self.current_frame_index = 0
                    if len(self.queue)==0:

                        self.subtitle_text = "Space tuşuna basılı tutarak konuşun..."
                        # default olarak kapalı ağız resmi göster ve subtilte'ı temizle
                    self.draw_image_centered(self.closed_img)
                    self.draw_subtitle(self.subtitle_text)
                else:
                    
                    state = self.mouth_states[self.current_frame_index % len(self.mouth_states)]
                    img = self.open_img if state == 'open' else self.closed_img

                    # Altyazı ekle
                    
                    self.current_frame_index += 1
                    self.draw_image_centered(img)

                    self.draw_subtitle(self.subtitle_text)

                pygame.display.flip()
            self.clock.tick(self.fps)

    def close_program(self):
        self.closed = True
        pygame.quit()