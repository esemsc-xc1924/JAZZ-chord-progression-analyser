from music21 import converter, harmony

def extract_chord_progression(musicxml_file):
    try:
        score = converter.parse(musicxml_file)
    except Exception as e:
        print(f"Error parsing {musicxml_file}: {e}")
        return []

    chords = []

    for element in score.recurse():
        if isinstance(element, harmony.ChordSymbol):
            chords.append(element.figure)  # Extract explicit chord notation

    print(f"Chords extracted from {musicxml_file}: {chords}")  # Debugging output
    return chords
