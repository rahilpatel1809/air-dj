import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

class AudioEngine:
    def __init__(self, filepath, deck_name):
        self.deck_name = deck_name
        self.filepaths = [filepath]
        self.track_index = 0
        self.load_track(self.filepaths[self.track_index])
        self.is_playing = False
        self.volume = 1.0
        self.pitch_shift = 1.0
        self.lock = threading.Lock()

        # Gesture-specific cooldown tracking
        self.last_action_time = {
            "toggle": 0,
            "volume": 0,
            "speed": 0,
            "fade": 0,
            "load": 0
        }
        self.cooldowns = {
            "toggle": 0.3,
            "volume": 0.0,
            "speed": 0.0,
            "fade": 0.7,
            "load": 1.0
        }

        # Global cross-gesture cooldown
        self.global_last_action = 0
        self.global_cooldown = 1

    def load_track(self, filepath):
        self.data, self.samplerate = sf.read(filepath, dtype='float32')
        self.pointer = 0
        self.is_playing = False
        print(f"[Deck {self.deck_name}] Loaded track: {filepath}")

    def next_track(self):
        if self.can_trigger("load"):
            self.track_index = (self.track_index + 1) % len(self.filepaths)
            self.load_track(self.filepaths[self.track_index])

    def previous_track(self):
        if self.can_trigger("load"):
            self.track_index = (self.track_index - 1) % len(self.filepaths)
            self.load_track(self.filepaths[self.track_index])

    def add_track(self, filepath):
        self.filepaths.append(filepath)

    def audio_callback(self, outdata, frames, time_, status):
        with self.lock:
            if not self.is_playing:
                outdata[:] = np.zeros((frames, self.data.shape[1]))
                return

            adjusted_frames = int(frames * self.pitch_shift)
            end = self.pointer + adjusted_frames
            chunk = self.data[self.pointer:end]

            if self.pitch_shift != 1.0:
                indices = np.linspace(0, len(chunk) - 1, frames)
                chunk = np.interp(indices, np.arange(len(chunk)), chunk[:, 0])
                chunk = np.expand_dims(chunk, axis=1)
            if chunk.shape[1] == 1:
                chunk = np.repeat(chunk, self.data.shape[1], axis=1)

            chunk *= self.volume
            if len(chunk) < frames:
                chunk = np.pad(chunk, ((0, frames - len(chunk)), (0, 0)), mode='constant')
                self.is_playing = False

            outdata[:] = chunk
            self.pointer += adjusted_frames

    def start(self):
        self.stream = sd.OutputStream(callback=self.audio_callback, samplerate=self.samplerate, channels=self.data.shape[1])
        self.stream.start()

    def can_trigger(self, action):
        now = time.time()

        if action in ["volume", "speed"]:
            return True

        if now - self.global_last_action < self.global_cooldown:
            return False

        if now - self.last_action_time[action] > self.cooldowns[action]:
            self.last_action_time[action] = now
            self.global_last_action = now
            return True

        return False

    def pause(self):
        self.is_playing = False
        print(f"[Deck {self.deck_name}] Paused")

    def resume(self):
        self.is_playing = True
        print(f"[Deck {self.deck_name}] Resumed")

    def toggle(self):
        if self.can_trigger("toggle"):
            if self.is_playing:
                self.pause()
            else:
                self.resume()

    def adjust_volume(self, vol):
        with self.lock:
            self.volume += vol
            self.volume = max(0, min(1, self.volume))
            print(f"[Deck {self.deck_name}] Volume adjusted to {self.volume:.2f}")

    def fade_out(self):
        if self.can_trigger("fade"):
            with self.lock:
                for i in range(10, -1, -1):
                    self.volume = i / 10.0
                    print(f"[Deck {self.deck_name}] Fading out... Volume: {self.volume:.2f}")
                    time.sleep(0.1)

    def fade_in(self):
        if self.can_trigger("fade"):
            with self.lock:
                for i in range(0, 11):
                    self.volume = i / 10.0
                    print(f"[Deck {self.deck_name}] Fading in... Volume: {self.volume:.2f}")
                    time.sleep(0.1)

    def adjust_speed(self, delta):
        with self.lock:
            self.speed += delta
            self.speed = max(0.5, min(2.0, self.speed))
            print(f"[Deck {self.deck_name}] Speed (playback speed) set to {self.speed:.2f}")