# MIDI ML Project

This repository contains scripts for extracting chord progressions from MIDI files, cleaning the data, classifying the mood of each progression, and training machine learning models.

## Installation

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

These dependencies include libraries such as `pretty_midi`, `music21`, `numpy`, `scikit-learn`, `matplotlib`, and `gensim` used throughout the project.

## Overview

The project workflow is split across several scripts:

- `1extract_midi_chords.py` – Extracts chord progressions from MIDI files.
- `dataset_cleaning.py` – Deduplicates and cleans the dataset.
- `3post_process_py` – Normalizes and filters the extracted chords.
- `4classify_moods.py` – Assigns mood labels based on chord progressions.
- `5analyze_results.py` – Analyzes mood classification results.
- `6preprocess_mood.py` – Converts data for machine learning.
- `7train_predict_moods_forest.py` – Trains a Random Forest classifier.
- `8final_model.py` – Final model and chord progression suggestions.

Each script can be run individually once the dataset paths are configured.
