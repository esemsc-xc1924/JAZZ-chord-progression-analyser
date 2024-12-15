import os
import json
import sqlite3
import music21

# Directory containing MusicXML files
dataset_dir = "/Users/xingchenchen/Desktop/JAZZ-chord-progression-analyser/dataset_demo"

# SQLite database file
db_path = "songs.db"

# Initialize the database
def initialize_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            chord_progression TEXT NOT NULL,
            sheet_music_link TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to process a single MusicXML file
def process_musicxml(file_path):
    try:
        score = music21.converter.parse(file_path)
        song_name = score.metadata.title if score.metadata and score.metadata.title else os.path.basename(file_path)
        chords = []

        # Extract chord progression
        for element in score.recurse():
            if isinstance(element, music21.harmony.ChordSymbol):
                chords.append(element.figure)

        print(f"Extracted {len(chords)} chords from {file_path}")
        print(chords)
        return {
            "name": song_name,
            "chords": chords,
            "sheet_music_link": file_path  # Store the file path as the link
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

# Store song data in the database
def store_song_in_db(song_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO songs (name, chord_progression, sheet_music_link)
        VALUES (?, ?, ?)
    ''', (song_data["name"], json.dumps(song_data["chords"]), song_data["sheet_music_link"]))
    conn.commit()
    conn.close()

# Process all MusicXML files in the directory
def process_all_files():
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".musicxml"):
            file_path = os.path.join(dataset_dir, filename)
            song_data = process_musicxml(file_path)
            if song_data:
                store_song_in_db(song_data)
                print(f"Stored: {song_data['name']}")

# Initialize database and process files
initialize_database()
process_all_files()
