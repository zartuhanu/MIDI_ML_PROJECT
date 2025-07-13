# MIDI Machine Learning Pipeline

This project extracts chord progressions from MIDI files, cleans the results, assigns a mood label, and trains machine learning models.

## Pipeline Overview
1. **Extraction** – `1extract_midi_chords.py` scans a MIDI dataset and writes detected progressions to `small_midi_chords_dataset.json`.
2. **Cleaning** – `3post_process_py` standardizes chord names and filters noisy data, producing `cleaned_midi_chords_dataset.json`.
3. **Classification** – `4classify_moods.py` analyzes the cleaned progressions and labels each one with a mood, saving to `mood_labeled_chords.json`.
4. **Training** – `6preprocess_mood.py` converts chords to scale degrees for ML input. `7train_predict_moods_forest.py` then trains a Random Forest model and outputs `ml_final_chords.json`. The script `8final_model.py` provides a more advanced model using word embeddings.

## Required Packages
- `pretty_midi`
- `music21`
- `scikit-learn`
- `gensim`
- `matplotlib`
- `numpy`

Install them with pip:
```bash
pip install pretty_midi music21 scikit-learn gensim matplotlib numpy
```

## Example Usage
The scripts contain path variables for the dataset and intermediate files. Edit these variables or pass your own paths when running the scripts.

```bash
# 1. (Optional) Deduplicate a dataset
python dataset_cleaning.py  # edit source_dataset/target_dataset inside the file

# 2. Extract progressions from your MIDI dataset
python 1extract_midi_chords.py  # set dataset_path at the top of the script

# 3. Clean the extracted progressions
python 3post_process_py

# 4. Classify moods for each progression
python 4classify_moods.py

# 5. Preprocess for machine learning and train the model
python 6preprocess_mood.py
python 7train_predict_moods_forest.py

# 6. (Optional) Train the final model with embeddings
python 8final_model.py
```

`dataset_path` in `1extract_midi_chords.py` should point to your MIDI folder. `dataset_cleaning.py` uses `source_dataset` and `target_dataset` variables to specify input and output directories.
