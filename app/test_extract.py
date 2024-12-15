from chord_extraction import extract_chord_progression

def test_extract_chords():
    test_file = "/Users/xingchenchen/Desktop/JAZZ-chord-progression-analyser/dataset_demo/Love Me Or Leave Me.musicxml"  # Replace with an actual file path

    try:
        print(f"Testing extraction for file: {test_file}")
        chords = extract_chord_progression(test_file)
        if chords:
            print(f"Test passed! Extracted chords: {chords}")
        else:
            print(f"Test failed. No chords extracted from {test_file}.")
    except Exception as e:
        print(f"Test failed with an error: {e}")

if __name__ == "__main__":
    test_extract_chords()
