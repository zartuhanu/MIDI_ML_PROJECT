import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

# Load the cleaned chord progressions
input_file = "cleaned_midi_chords_dataset.json"
output_file = "mood_labeled_chords.json"

# Enharmonic mapping to ensure consistency
enharmonic_map = {
    "C#": "Db", "Db": "Db",
    "D#": "Eb", "Eb": "Eb",
    "F#": "Gb", "Gb": "Gb",
    "G#": "Ab", "Ab": "Ab",
    "A#": "Bb", "Bb": "Bb"
}

def normalize_chord(chord):
    """Standardizes chord names and resolves enharmonic equivalents."""
    chord = re.sub(r"(maj7|m7|7|sus4|dim|aug|m9|9|11|13)$", "", chord)  # Remove extensions
    root = re.match(r"[A-G]#?|[A-G]b?", chord)  # Extract root note
    if root:
        root = root.group()
        return enharmonic_map.get(root, root)  # Convert to a consistent form
    return chord

def convert_to_scale_degrees(chords, key):
    """Converts chords to relative scale degrees with fallback for accidentals."""
    chromatic_scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    root_note = key.split()[0]
    is_minor = "minor" in key
    
    if root_note not in chromatic_scale:
        return []  # If the key is unknown or invalid, return empty
    
    root_index = chromatic_scale.index(root_note)
    shifted_scale = chromatic_scale[root_index:] + chromatic_scale[:root_index]  # Rotate scale
    
    relative_degrees = []
    for chord in chords:
        normalized_chord = normalize_chord(chord)
        if normalized_chord in shifted_scale:
            degree = shifted_scale.index(normalized_chord) + 1
            relative_degrees.append(degree)
    
    return tuple(relative_degrees) if relative_degrees else (1,)  # Default to tonic if empty

def find_best_match(scale_degrees):
    best_match = "Unknown"
    best_score = 0
    for pattern, mood in mood_mappings.items():
        score = SequenceMatcher(None, scale_degrees, pattern).ratio()
        if score > best_score and score > 0.4:  # Lowered threshold for better generalization
            best_match = mood
            best_score = score
    return best_match

# Expanded common chord progression patterns and their moods
mood_mappings = {
    (1, 5, 6, 4): "Uplifting, Hopeful",
    (6, 4, 1, 5): "Somber, Emotional",
    (1, 6, 4, 5): "Uplifting, Feel-Good",
    (4, 5, 1, 6): "Cyclical, Unresolved",
    (2, 5, 1): "Jazzy, Smooth",
    (1, 4, 5): "Strong, Upbeat",
    (1, 4, 6, 5): "Warm, Nostalgic",
    (1, 5, 2, 6): "Melancholic",
    (6, 2, 5, 1): "Reflective, Dreamy",
    (1, 3, 4, 5): "Sentimental, Thoughtful",
}

# Track removed progressions
filtered_count = 0
unknown_progressions = []

# Process each song and classify its mood
mood_labeled_data = {}
for song, data in json.load(open(input_file)).items():
    key = data.get("key", "Unknown")
    progression = data.get("progression", [])
    
    if key != "Unknown" and progression:
        scale_degrees = convert_to_scale_degrees(progression, key)
        mood = find_best_match(scale_degrees)
        
        if mood == "Unknown":
            filtered_count += 1
            unknown_progressions.append({"song": song, "key": key, "progression": progression, "scale_degrees": scale_degrees})
        
        mood_labeled_data[song] = {
            "key": key,
            "progression": progression,
            "mood": mood
        }
    else:
        filtered_count += 1
        unknown_progressions.append({"song": song, "key": key, "progression": progression})
        mood_labeled_data[song] = {"key": key, "progression": progression, "mood": "Unknown"}

# Print filtering information
print(f"Total progressions processed: {len(mood_labeled_data)}")
print(f"Total progressions labeled with a mood: {len(mood_labeled_data) - filtered_count}")
print(f"Total progressions marked as Unknown: {filtered_count}")

# Save the labeled dataset
with open(output_file, "w") as f:
    json.dump(mood_labeled_data, f, indent=4)

# Save unknown progressions for further debugging
with open("unknown_progressions.json", "w") as f:
    json.dump(unknown_progressions, f, indent=4)

print(f"Mood classification completed. Results saved to {output_file}")
print(f"Unknown progressions saved to unknown_progressions.json")
