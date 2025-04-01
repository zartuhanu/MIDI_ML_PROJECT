import json
import numpy as np
import re

# Load mood-labeled chord progressions
input_file = "mood_labeled_chords.json"
output_file = "ml_ready_chords.json"
removed_output_file = "removed_progressions2.json"

with open(input_file, "r") as f:
    chord_data = json.load(f)

# Define major and minor scales
MAJOR_SCALE = ["C", "D", "E", "F", "G", "A", "B"]
MINOR_SCALE = ["C", "D", "Eb", "F", "G", "Ab", "Bb"]

# Enharmonic mapping for consistent scale conversion
enharmonic_map = {
    "C#": "Db", "Db": "Db",
    "D#": "Eb", "Eb": "Eb",
    "F#": "Gb", "Gb": "Gb",
    "G#": "Ab", "Ab": "Ab",
    "A#": "Bb", "Bb": "Bb"
}

# Predefined progressions that should bypass filtering
BYPASS_PROGRESSIONS = {(2, 5, 1), (1, 4, 5)}

def normalize_chord(chord):
    """Standardizes chord names and resolves enharmonic equivalents."""
    root = re.match(r"[A-G]#?|[A-G]b?", chord)
    if root:
        root = root.group()
        return enharmonic_map.get(root, root)  # Convert to a consistent form
    return chord

def chord_to_degrees(chords, key):
    """Converts chord names to scale degrees relative to the key, handling inversions and accidentals."""
    if key == "Unknown" or not chords:
        return []  # Skip unknown keys
    
    root = key.split()[0]  # Extract tonic
    is_minor = "minor" in key
    scale = MINOR_SCALE if is_minor else MAJOR_SCALE
    
    if root not in scale:
        return []  # If the root is not found, skip
    
    root_index = scale.index(root)
    rotated_scale = scale[root_index:] + scale[:root_index]  # Shift scale to start at tonic
    
    degrees = []
    for chord in chords:
        normalized_chord = normalize_chord(chord)
        base_note = re.match(r"[A-G]#?|[A-G]b?", normalized_chord)
        if base_note and base_note.group() in rotated_scale:
            degree = rotated_scale.index(base_note.group()) + 1
            degrees.append(degree)
    
    return degrees if degrees else [1]  # Default to tonic if no mapping found

def remove_duplicate_scale_degrees(degrees):
    """Removes duplicate scale degrees while preserving order."""
    return list(dict.fromkeys(degrees))

# Track counts
total_progressions = len(chord_data)
kept_progressions = 0
filtered_progressions = 0
removed_progressions = []

# Convert dataset
ml_data = []
for song, data in chord_data.items():
    key = data.get("key", "Unknown")
    progression = data.get("progression", [])
    mood = data.get("mood", "Unknown")
    
    degrees = chord_to_degrees(progression, key)
    degrees = remove_duplicate_scale_degrees(degrees)  # Remove duplicate scale degrees
    
    # Convert to tuple for bypass check
    degrees_tuple = tuple(degrees)
    
    # Filter out progressions with fewer than 3 unique chords unless they match bypass criteria
    if len(set(degrees)) >= 3 or degrees_tuple in BYPASS_PROGRESSIONS:
        ml_data.append({"degrees": degrees, "mood": mood})
        kept_progressions += 1
    else:
        filtered_progressions += 1
        removed_progressions.append({"song": song, "key": key, "progression": progression, "degrees": degrees})

# Save processed data for ML model
with open(output_file, "w") as f:
    json.dump(ml_data, f, indent=4)

# Save removed progressions for review
with open(removed_output_file, "w") as f:
    json.dump(removed_progressions, f, indent=4)

# Print tracking information
print(f"Total progressions processed: {total_progressions}")
print(f"Total progressions kept for ML: {kept_progressions}")
print(f"Total progressions filtered out: {filtered_progressions}")
print(f"Preprocessed data saved to {output_file}")
print(f"Removed progressions saved to {removed_output_file}")
