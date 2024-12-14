from music21 import key, roman

major_keys = [
    "C",  # No sharps or flats
    "G",  # 1 sharp
    "D",  # 2 sharps
    "A",  # 3 sharps
    "E",  # 4 sharps
    "B",  # 5 sharps
    "F#",  # 6 sharps
    "C#",  # 7 sharps
    "F",  # 1 flat
    "Bb",  # 2 flats
    "Eb",  # 3 flats
    "Ab",  # 4 flats
    "Db",  # 5 flats
    "Gb",  # 6 flats
    "Cb"  # 7 flats
]


def triad_name_from_roman(roman_numeral):
    root_name = roman_numeral.root().name
    quality = roman_numeral.quality

    # Map the chord quality to a short suffix
    if quality == 'major':
        return root_name
    elif quality == 'minor':
        return root_name + 'm'
    elif quality == 'diminished':
        return root_name + 'dim'
    elif quality == 'augmented':
        return root_name + 'aug'
    else:
        return root_name  # fallback


# Precompute diatonic chords for all keys
diatonic_chords_dict = {}
for k in major_keys:
    k_obj = key.Key(k)
    chord_degrees = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    chord_names = []
    for deg in chord_degrees:
        rn = roman.RomanNumeral(deg, k_obj)
        chord_names.append(triad_name_from_roman(rn))
    diatonic_chords_dict[k] = chord_names


def get_diatonic_chords(major_key):
    if major_key in diatonic_chords_dict:
        return diatonic_chords_dict[major_key]
    else:
        raise ValueError(f"Invalid key: {major_key}. Please select a valid major key.")


# Example usage
selected_key = "C"
print(f"Diatonic chords for {selected_key}: {get_diatonic_chords(selected_key)}")

# Display the matrix
for scale, chords in diatonic_chords_dict.items():
    print(f"{scale}: {chords}")