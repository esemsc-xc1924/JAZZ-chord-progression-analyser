import music21

# Load the MusicXML file using music21
file_path = 'Watermelon Man.musicxml'  # Update the path to your file
score = music21.converter.parse(file_path)

# Extract song metadata and chords
song_name = score.metadata.title if score.metadata and score.metadata.title else "Unknown"
chords = []

# Iterate through the elements to find chords (harmony objects)
for element in score.recurse():
    if isinstance(element, music21.harmony.ChordSymbol):
        chords.append(element.figure)

# Compile the extracted data into a dictionary
song_data = {
    "song_name": song_name,
    "chords": chords
}

# Print as JSON
import json
print(json.dumps(song_data, indent=2))
