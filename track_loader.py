import os

class TrackLoader:
    @staticmethod
    def load_all_tracks():
        folder = "./tracks"
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith((".wav", ".mp3"))]
        if not files:
            raise Exception("No audio files found in the ./tracks folder.")
        return files

    @staticmethod
    def select_tracks(files):
        print("\nAvailable Tracks:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {os.path.basename(file)}")

        selected = input("\nEnter track numbers to load (e.g., 1 2): ").split()
        indices = [int(i) - 1 for i in selected if i.isdigit() and 0 < int(i) <= len(files)]
        
        if not indices:
            print("No valid tracks selected. Defaulting to first one.")
            return files[0], None  # fallback

        elif len(indices) == 1:
            return files[indices[0]], None

        elif len(indices) >= 2:
            return files[indices[0]], files[indices[1]]
