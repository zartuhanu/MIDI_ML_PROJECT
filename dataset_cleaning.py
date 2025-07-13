import os
import re
import shutil
import csv
from collections import defaultdict
import argparse

def normalize_filename(filename):
    return re.sub(r'\.\d+(?=\.mid$)', '', filename)

def deduplicate_midi_dataset_by_length_with_logging(source_root, target_root, log_file="deduplication_log.csv"):
    if not os.path.exists(target_root):
        os.makedirs(target_root)

    log_entries = []

    for artist in os.listdir(source_root):
        artist_path = os.path.join(source_root, artist)
        if not os.path.isdir(artist_path):
            continue

        target_artist_path = os.path.join(target_root, artist)
        os.makedirs(target_artist_path, exist_ok=True)

        song_map = defaultdict(list)
        for filename in os.listdir(artist_path):
            if filename.endswith(".mid"):
                norm_name = normalize_filename(filename)
                full_path = os.path.join(artist_path, filename)
                file_size = os.path.getsize(full_path)
                song_map[norm_name].append((filename, file_size))

        for norm_name, file_list in song_map.items():
            file_list.sort(key=lambda x: x[1], reverse=True)
            best_file, best_size = file_list[0]
            src_file = os.path.join(artist_path, best_file)
            dest_file = os.path.join(target_artist_path, norm_name)
            shutil.copy2(src_file, dest_file)

            skipped_files = [f for f, s in file_list[1:]]
            log_entries.append({
                "artist": artist,
                "normalized_song_name": norm_name,
                "kept_file": best_file,
                "kept_file_size": best_size,
                "skipped_files": "; ".join(skipped_files)
            })

            print(f"✔ Copied: {src_file} → {dest_file}")

    # Save log to CSV
    with open(log_file, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["artist", "normalized_song_name", "kept_file", "kept_file_size", "skipped_files"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in log_entries:
            writer.writerow(entry)

    print(f"\n📝 Log saved to: {log_file}")

def main():
    parser = argparse.ArgumentParser(description="Deduplicate MIDI files by length")
    parser.add_argument("source_dataset", help="Path to the source dataset directory")
    parser.add_argument("target_dataset", help="Directory to store the deduplicated dataset")
    parser.add_argument("--log-file", default="deduplication_log.csv", help="Path for the CSV log file")
    args = parser.parse_args()

    deduplicate_midi_dataset_by_length_with_logging(
        args.source_dataset, args.target_dataset, args.log_file
    )


if __name__ == "__main__":
    main()
