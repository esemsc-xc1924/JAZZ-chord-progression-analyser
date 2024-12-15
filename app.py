from flask import Flask, render_template, request, jsonify, send_from_directory
from music21 import key, chord, stream, midi, duration, tempo, pitch
from midi2audio import FluidSynth
from pydub import AudioSegment
import re

import os
print(os.getcwd())
app = Flask(__name__)

# Directory to store generated audio files
AUDIO_DIR = "static/sounds"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Path to the SoundFont file
SOUNDFONT_PATH = "/Users/wangziyi/Desktop/JAZZ-chord-progression-analyser/GeneralUserGSv1.471.sf2"
SOUNDFONT_PATH = "GeneralUserGSv1.471.sf2"
fs = FluidSynth(SOUNDFONT_PATH)

# Backend default settings for chord duration and tempo
DEFAULT_CHORD_DURATION = 1  # 2 quarter notes (e.g., 2 seconds at 60 BPM)
DEFAULT_TEMPO_BPM = 120     # Tempo in beats per minute

@app.route("/")
def index():
    return render_template("index.html")

def trim_trailing_silence(wav_file, trim_duration=2000):
    """
    Trims a specified duration from the end of a WAV file.

    Args:
        wav_file (str): Path to the WAV file.
        trim_duration (int): Duration to trim from the end (in milliseconds).
    """
    # Load the audio file
    audio = AudioSegment.from_file(wav_file, format="wav")

    # Calculate the new end point
    trimmed_audio = audio[:-trim_duration] if len(audio) > trim_duration else audio

    # Save the trimmed audio back to the file
    trimmed_audio.export(wav_file, format="wav")

# Function to generate a chord as a WAV file
def generate_chord_audio_old(selected_key, selected_chord):
    """
    Generates a chord MIDI and converts it to a WAV file in root position.

    Args:
        selected_key (str): The musical key (e.g., "C").
        selected_chord (str): The chord type (e.g., "I").

    Returns:
        str: Path to the generated WAV file.
    """
    # Map chord types to intervals (in semitones)
    roman_to_intervals = {
        "I": [0, 4, 7],        # Major
        "ii": [0, 3, 7],       # Minor
        "iii": [0, 3, 7],      # Minor
        "IV": [0, 4, 7],       # Major
        "V": [0, 4, 7],        # Major
        "vi": [0, 3, 7],       # Minor
        "vii°": [0, 3, 6],     # Diminished
    }

    # Get the root MIDI note for the selected scale degree
    music_key = key.Key(selected_key)
    scale_degrees = {
        "I": 1, "ii": 2, "iii": 3, "IV": 4, "V": 5, "vi": 6, "vii°": 7
    }
    root_degree = scale_degrees[selected_chord]
    root_pitch = music_key.pitchFromDegree(root_degree)  # Get the pitch
    root_midi = root_pitch.midi  # Get MIDI note number
    print(f"Selected chord: {selected_chord}, Root MIDI: {root_midi}")

    # Adjust octave for high-pitched keys (F and above)
    if selected_key in ["F", "F#", "Gb", "G", "G#", "Ab", "A", "Bb", "B"]:
        root_midi -= 12  # Lower by one octave


    # Construct the chord in root position using intervals
    intervals = roman_to_intervals[selected_chord]
    chord_midi_notes = [root_midi + interval for interval in intervals]

    # Create a music21 chord object
    music_chord = chord.Chord(chord_midi_notes)
    music_chord.duration = duration.Duration(DEFAULT_CHORD_DURATION)

    # Create a music21 Stream and set the tempo
    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=DEFAULT_TEMPO_BPM))
    s.append(music_chord)

    selected_key_clean = selected_key.replace("#", "sharp")
    # Generate MIDI and WAV filenames
    midi_filename = f"{AUDIO_DIR}/{selected_key_clean}_{selected_chord}.mid"
    wav_filename = midi_filename.replace(".mid", ".wav")

    # Write MIDI file
    mf = midi.translate.music21ObjectToMidiFile(s)
    mf.open(midi_filename, "wb")
    mf.write()
    mf.close()

    # Convert MIDI to WAV using FluidSynth
    fs.midi_to_audio(midi_filename, wav_filename)

    # Trim trailing silence from the WAV file
    trim_trailing_silence(wav_filename, trim_duration=3000)

    return wav_filename


def get_base_chord(selected_chord):
    # Match a chord suffix pattern and remove it
    match = re.match(r"([A-Ga-g#b\d]+)(maj7|7b9|7b13|7|9|13|6|dim|m7|m|half-dim)?", selected_chord)
    return match.group(1) if match else selected_chord


def generate_chord_audio(selected_key, selected_chord=None):
    """
    Generates a chord MIDI and converts it to a WAV file in root position.

    Args:
        selected_key (str): The musical key (e.g., "C").
        selected_chord (str): The chord type or alteration (e.g., "I", "maj7", "7b9").

    Returns:
        str: Path to the generated WAV file.
    """
    # Base intervals for triads
    chord_intervals = {
        "maj": [0, 4, 7],  # Major triad
        "m": [0, 3, 7],    # Minor triad
        "dim": [0, 3, 6],  # Diminished triad
    }

    # Extensions and alterations (added to the base triads)
    alterations = {
        "maj7": [11],       # Major 7th
        "7": [10],          # Dominant 7th
        "7b9": [10, 13],    # Dominant 7th with flat 9
        "7b13": [10, 20],   # Dominant 7th with flat 13
        "maj9": [11, 14],   # Major 9th
        "min7": [10],       # Minor 7th
        "min9": [10, 14],   # Minor 9th
        "min6": [9],        # Minor 6th
        "min11": [10, 17],  # Minor 11th
        "min13": [10, 21],  # Minor 13th
        "dim7": [9],        # Diminished 7th
        "half-dim": [10],   # Half-diminished 7th
    }

    # Handle basic scale degrees (e.g., "I", "ii", "IV")
    roman_to_scale = {
        "I": ("maj", [1]), "ii": ("m", [2]), "iii": ("m", [3]),
        "IV": ("maj", [4]), "V": ("maj", [5]), "vi": ("m", [6]), "vii°": ("dim", [7])
    }
    print("selected_chord",selected_chord)
    # If the selected chord is a degree (e.g., "I", "ii"), map it to a base chord
    if selected_chord in roman_to_scale:
        base_chord, scale_degrees = roman_to_scale[selected_chord]
        alteration = None
    else:
        # Extract base chord and alteration (for extended chords like "maj7")
        base_chord = get_base_chord(selected_chord) if selected_chord else None
        alteration = selected_chord[len(base_chord):] if selected_chord else None

        # Determine scale degrees for unknown or custom chords
        if base_chord in roman_to_scale:
            base_chord, scale_degrees = roman_to_scale[base_chord]
        else:
            # Default to major triad if unknown
            base_chord = "maj"
            scale_degrees = [1]

    print(f"Base chord: {base_chord}, Scale degrees: {scale_degrees}, Alteration: {alteration}")

    # Extract base chord and alteration
    #base_chord = get_base_chord(selected_chord) if selected_chord else None
    #alteration = selected_chord[len(base_chord):] if selected_chord else None

    # Determine chord type and intervals
    #if base_chord in roman_to_scale:
    #    chord_type, scale_degrees = roman_to_scale[base_chord]
    #else:
        # Default to major for unknown cases
    #    chord_type = "maj"
    #    scale_degrees = [1]

    # Get the root MIDI note
    music_key = key.Key(selected_key)
    root_midi = music_key.pitchFromDegree(scale_degrees[0]).midi

    # Adjust octave for higher keys
    if selected_key in ["F", "F#", "G", "Ab", "A", "Bb", "B"]:
        root_midi -= 12  # Lower by one octave

    # Construct the base chord in root position
    base_intervals = chord_intervals.get(base_chord, [])
    chord_midi_notes = [root_midi + interval for interval in base_intervals]
    print("base_intervals", base_intervals)

    # Add extensions or alterations if specified
    if alteration:
        extension_intervals = alterations.get(alteration, [])
        chord_midi_notes += [root_midi + interval for interval in extension_intervals]
    
    print(f"Chord MIDI notes: {chord_midi_notes}")
    # Convert MIDI notes to note names
    chord_note_names = [pitch.Pitch(midi).nameWithOctave for midi in chord_midi_notes]
    # Debug: Print chord notes
    print(f"Chord note names: {chord_note_names}")
    # Create a music21 chord object
    music_chord = chord.Chord(chord_midi_notes)
    music_chord.duration = duration.Duration(DEFAULT_CHORD_DURATION)

    # Create a music21 Stream and set the tempo
    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=DEFAULT_TEMPO_BPM))
    s.append(music_chord)

    selected_key_clean = selected_key.replace("#", "sharp")
    # Generate MIDI and WAV filenames
    midi_filename = f"{AUDIO_DIR}/{selected_key_clean}_{selected_chord}.mid"
    wav_filename = midi_filename.replace(".mid", ".wav")

    # Write MIDI file
    mf = midi.translate.music21ObjectToMidiFile(s)
    mf.open(midi_filename, "wb")
    mf.write()
    mf.close()

    # Convert MIDI to WAV using FluidSynth
    fs.midi_to_audio(midi_filename, wav_filename)

    # Trim trailing silence from the WAV file
    trim_trailing_silence(wav_filename, trim_duration=3000)

    return wav_filename


# Handle chord generation requests
@app.route("/generate_chord", methods=["POST"])
def generate_chord():
    data = request.get_json()
    selected_key = data.get("key")
    selected_chord = data.get("chord")

    try:
        # Generate the chord audio file
        audio_file = generate_chord_audio(selected_key, selected_chord)
        return jsonify({"status": "success", "audio_file": f"/{audio_file}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Serve audio files
@app.route("/static/sounds/<filename>")
def serve_audio_file(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
