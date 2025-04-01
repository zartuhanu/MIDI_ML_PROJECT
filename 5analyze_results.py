import json

# Load the mood-labeled dataset
input_file = "mood_labeled_chords.json"

with open(input_file, "r") as f:
    moods = json.load(f)

# Count the number of 'unknown' mood classifications
unknown_count = sum(1 for data in moods.values() if data["mood"] == "Unknown")
total_samples = len(moods)
unknown_percentage = (unknown_count / total_samples) * 100 if total_samples > 0 else 0

print(f"Total 'Unknown' classifications: {unknown_count} / {total_samples} ({unknown_percentage:.2f}% unknown)")

# Print some sample mood classifications
sample_files = list(moods.keys())[:5]
for midi_path in sample_files:
    print(f"\nMIDI File: {midi_path}")
    print(f"Assigned Mood: {moods[midi_path]['mood']}")
