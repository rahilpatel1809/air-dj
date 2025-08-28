from gesture_controller import GestureController
from audio_engine import AudioEngine
from track_loader import TrackLoader
import threading

# Load all tracks and let user choose
all_tracks = TrackLoader.load_all_tracks()
deck_a_file, deck_b_file = TrackLoader.select_tracks(all_tracks)

# Initialize Deck A
deck_a = AudioEngine(deck_a_file, deck_name="A")

# Initialize Deck B if selected
deck_b = AudioEngine(deck_b_file, deck_name="B") if deck_b_file else None

# Start gesture controller
gesture_controller = GestureController(deck_a, deck_b)
gesture_thread = threading.Thread(target=gesture_controller.run)
gesture_thread.start()

# Start audio playback
deck_a.start()
if deck_b:
    deck_b.start()

gesture_thread.join()