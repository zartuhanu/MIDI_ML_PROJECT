import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from collections import Counter
import random

# Load the preprocessed dataset
input_file = "ml_ready_chords.json"
output_file = "ml_final_chords.json"

with open(input_file, "r") as f:
    chord_data = json.load(f)

# Separate labeled and unknown mood data
labeled_data = []
unknown_data = []

for entry in chord_data:
    if entry["mood"] != "Unknown":
        labeled_data.append(entry)
    else:
        unknown_data.append(entry)

# Define a fixed progression length (padding or truncating)
MAX_LENGTH = 8  # Adjust as needed

def pad_or_truncate(progression, length=MAX_LENGTH):
    """Ensures all progressions have the same length."""
    if len(progression) < length:
        return progression + [0] * (length - len(progression))  # Pad with 0s
    return progression[:length]  # Truncate if too long

# Prepare training data
X = [pad_or_truncate(entry["degrees"]) for entry in labeled_data]
y = [entry["mood"] for entry in labeled_data]

# Split dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model performance
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Generate confusion matrix
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot(cmap="Blues", values_format=".0f")
plt.title("Random Forest Model Error Analysis")
plt.show()

# Predict moods for unknown data
for entry in unknown_data:
    processed_degrees = pad_or_truncate(entry["degrees"])
    predicted_mood = model.predict([processed_degrees])[0]
    entry["mood"] = predicted_mood  # Assign predicted mood

# Merge the datasets back together
final_dataset = labeled_data + unknown_data

# Save the updated dataset with predicted moods
with open(output_file, "w") as f:
    json.dump(final_dataset, f, indent=4)

print(f"Predicted moods for unknown entries and saved to {output_file}")

# Debugging & Analysis
print("\n Running post-training analysis...")

# Count remaining "Unknown" moods
mood_counts = Counter(entry["mood"] for entry in final_dataset)
unknown_count = mood_counts.get("Unknown", 0)
total_entries = len(final_dataset)

print(f"Total Entries: {total_entries}")
print(f"Total 'Unknown' Moods Remaining: {unknown_count} ({(unknown_count / total_entries) * 100:.2f}%)")

# Plot mood distribution
plt.figure(figsize=(12, 6))
plt.bar(mood_counts.keys(), mood_counts.values(), color="royalblue")
plt.xticks(rotation=45, ha="right")
plt.ylabel("Frequency")
plt.title("Distribution of Predicted Moods")
plt.show()

# Spot-check random predictions
print("\n Randomly checking predictions:")
sample_predictions = random.sample(final_dataset, min(10, len(final_dataset)))
for entry in sample_predictions:
    print(f"Chord Progression: {entry['degrees']} -> Predicted Mood: {entry['mood']}")
