import os 
import pretty_midi   # type: ignore
import json
import collections
import re  # Import regex to remove octave numbers
from music21 import chord, key, meter, stream # type: ignore
import random

# Define the dataset path
dataset_path = "/Users/zartuhan/Documents/ML_Project/lmd_clean/"
midi_chords_data = {}

# Limit the number of files processed (for debugging)
MAX_FILES = 100  # Increased sample size
processed_count = 0

# Define harmonic instrument program numbers (MIDI standard)
HARMONIC_INSTRUMENTS = list(range(0, 8)) + list(range(24, 32)) + list(range(40, 48)) + list(range(80, 88))

# Collect all MIDI file paths
midi_files = []
for root, _, files in os.walk(dataset_path):
    for file in files:
        if file.endswith(".mid"):
            midi_files.append(os.path.join(root, file))

# Shuffle the list to ensure a wider selection of artists
random.shuffle(midi_files)

def simplify_chord_name(m21_chord):
    """Simplifies the chord name to standard notation (Cmaj, Dmin, G7, etc.)."""
    root = m21_chord.root().name  # Extract root note (C, D#, F, etc.)
    quality = m21_chord.quality  # Extract quality (major, minor, diminished, augmented)
    
    quality_map = {
        "major": "maj",
        "minor": "min",
        "diminished": "dim",
        "augmented": "aug",
        "dominant": "7",
        "half-diminished": "m7b5",
        "major-seventh": "maj7",
        "minor-seventh": "min7",
        "diminished-seventh": "dim7",
        "augmented-seventh": "aug7"
    }
    
    simplified_quality = quality_map.get(quality, "")
    return f"{root}{simplified_quality}" if simplified_quality else root

def detect_key_signature(midi_data):
    """Detects the key and mode of the MIDI file using music21 and removes accidental formatting issues."""
    try:
        s = stream.Score()
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                s.append(chord.Chord([note.pitch]))

        key_analysis = s.analyze("key")
        key_name = key_analysis.tonic.name  # Get the tonic note
        mode = "major" if key_analysis.mode == "major" else "minor"

        # Sanitize the output (remove any unexpected characters)
        key_name = key_name.replace("-", "")  # Fix cases like "A- major"

        return f"{key_name} {mode}"
    except:
        return "Unknown"


def find_main_harmonic_instrument(midi_data):
    """Finds the primary harmonic instrument (piano/guitar if available)."""
    instrument_chord_counts = {}
    for instrument in midi_data.instruments:
        if not instrument.is_drum and instrument.program in HARMONIC_INSTRUMENTS:
            unique_chords = set()
            for note in instrument.notes:
                note_name = pretty_midi.note_number_to_name(note.pitch)
                note_clean = re.sub(r"\d", "", note_name)
                unique_chords.add(note_clean)
            instrument_chord_counts[instrument] = len(unique_chords)
    
    if instrument_chord_counts:
        return max(instrument_chord_counts, key=instrument_chord_counts.get)
    return None

def extract_progressions(midi_file):
    """Extracts structured chord progressions from the most relevant harmonic instrument."""
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file)
        chords_by_measure = collections.defaultdict(list)
        
        # Detect key signature
        song_key = detect_key_signature(midi_data)
        
        # Find main harmonic instrument
        main_instrument = find_main_harmonic_instrument(midi_data)
        if not main_instrument:
            print(f"Skipping {midi_file} - No valid harmonic instrument found")
            return "Unknown", []

        # Extract chords from main instrument
        for note in main_instrument.notes:
            measure = int(note.start // 2)  # Group notes into measures (approx. 2 sec per measure)
            note_name = pretty_midi.note_number_to_name(note.pitch)
            note_clean = re.sub(r"\d", "", note_name)
            chords_by_measure[measure].append(note_clean)
                
        structured_progressions = []
        
        for measure, notes in sorted(chords_by_measure.items()):
            if len(notes) > 2:  # Only consider measures with at least a triad
                try:
                    m21_chord = chord.Chord(notes)
                    simplified_chord = simplify_chord_name(m21_chord)
                    if simplified_chord:
                        structured_progressions.append(simplified_chord)
                except:
                    pass  # Ignore errors
        
        # Ensure at least 2 unique chords in the detected progression
        unique_chords = list(set(structured_progressions))
        if len(unique_chords) < 2:
            print(f"Skipping {midi_file} - Only one unique chord detected")
            return song_key, []
        
        # Use the first repeating 4-8 chord sequence
        best_progression = structured_progressions[:8] if len(structured_progressions) >= 8 else structured_progressions
        
        if not best_progression:
            print(f"⚠ Warning: No valid repeating chord progression found in {midi_file}")
            return song_key, []
        
        return song_key, best_progression
    except Exception as e:
        print(f"Skipping {midi_file}: {e}")
        return "Unknown", []

# Process a limited number of MIDI files
output_file = "small_midi_chords_dataset.json"

for midi_path in midi_files[:MAX_FILES]:
    song_key, best_progression = extract_progressions(midi_path)
    if best_progression:
        midi_chords_data[midi_path] = {"key": song_key, "progression": best_progression}
        processed_count += 1
        print(f"Processed {processed_count}/{MAX_FILES}: {midi_path} ({song_key})")

# Final save
output_file = "small_midi_chords_dataset.json"
with open(output_file, "w") as f:
    json.dump(midi_chords_data, f, indent=4)

print(f"Processed {processed_count} MIDI files. Chord progressions saved to {output_file}.")
