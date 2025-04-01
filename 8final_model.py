import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import random
import gensim.downloader as api
from sklearn.metrics.pairwise import cosine_similarity

# Load the balanced dataset
input_file = "ml_final_chords.json"
with open(input_file, "r") as f:
    chord_data = json.load(f)

# Define a fixed progression length (padding or truncating)
MAX_LENGTH = 8  # Adjust as needed

def pad_or_truncate(progression, length=MAX_LENGTH):
    """Ensures all progressions have the same length."""
    return (progression + [0] * (length - len(progression)))[:length]

# Prepare data for ML model
X = [pad_or_truncate(entry["degrees"]) for entry in chord_data]  
y = [entry["mood"] for entry in chord_data]  

# Convert lists to NumPy arrays
X = np.array(X, dtype=np.float64)
y = np.array(y)

# Split dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate model performance
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Load pre-trained Word2Vec model
glove_vectors = api.load("word2vec-google-news-300")

def find_closest_mood(target_mood, known_moods):
    """Finds the closest available mood using Word2Vec similarity."""
    known_moods = list(known_moods)
    target_vector = glove_vectors[target_mood] if target_mood in glove_vectors else np.zeros(300)
    known_vectors = np.array([glove_vectors[mood] if mood in glove_vectors else np.zeros(300) for mood in known_moods])
    
    similarities = cosine_similarity([target_vector], known_vectors)[0]
    closest_match_index = np.argmax(similarities)
    
    return known_moods[closest_match_index]

def suggest_chord_progression(mood):
    """Predicts a chord progression based on mood using Word2Vec similarity and ML model."""
    
    if mood not in y_train:
        closest_mood = find_closest_mood(mood, set(y_train))
        print(f"⚠ '{mood}' not found. Using closest match: '{closest_mood}'")
        mood = closest_mood
    
    # Find matching chord progressions for predicted mood
    mood_index = np.where(y_train == mood)[0]
    
    if len(mood_index) > 0:
        suggested_progression = X_train[random.choice(mood_index)]
        return suggested_progression.tolist()
    
    return "❌ No suitable chord progression available."

# Example usage

example_mood = "Sad" 
predicted_progression = suggest_chord_progression(example_mood) 
print(f"Suggested chord progression for'{example_mood}': {predicted_progression}")
