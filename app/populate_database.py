import os
import psycopg2
from chord_extraction import extract_chord_progression

def populate_database(dataset_dir, connection):
    """
    Populates the PostgreSQL database with data from MusicXML files.

    Args:
        dataset_dir (str): Path to the directory containing MusicXML files.
        connection: PostgreSQL connection object.
    """
    cursor = connection.cursor()

    for filename in os.listdir(dataset_dir):
        if filename.endswith(".musicxml"):
            file_path = os.path.join(dataset_dir, filename)
            song_name = os.path.splitext(filename)[0]
            
            chord_progression = extract_chord_progression(file_path)

            if not chord_progression:
                print(f"No chords extracted for {file_path}. Skipping insertion.")
                continue

            try:
                cursor.execute(
                    """
                    INSERT INTO songs (song_name, file_path, chord_progression)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (file_path) DO NOTHING
                    """,
                    (song_name, file_path, chord_progression)
                )
            except Exception as e:
                print(f"Error inserting {file_path}: {e}")

    connection.commit()

if __name__ == "__main__":
    # Adjust the dataset directory and PostgreSQL credentials as needed
    dataset_dir = "/Users/xingchenchen/Desktop/JAZZ-chord-progression-analyser/dataset_demo"
    connection = psycopg2.connect("dbname=music user=xingchenchen password=yourpassword")

    populate_database(dataset_dir, connection)
    connection.close()
