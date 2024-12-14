from flask import Flask, render_template, request, jsonify, send_from_directory
from music21 import key, chord, stream, midi, duration, tempo
from midi2audio import FluidSynth
from pydub import AudioSegment

import os
print(os.getcwd())
app = Flask(__name__)

# Directory to store generated audio files
AUDIO_DIR = "static/sounds"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Path to the SoundFont file
SOUNDFONT_PATH = "/Users/wangziyi/Desktop/JAZZ-chord-progression-analyser/GeneralUserGSv1.471.sf2"
SOUNDFONT_PATH = "/Users/ege/Projects/JAZZ-chord-progression-analyser/GeneralUserGSv1.471.sf2"
fs = FluidSynth(SOUNDFONT_PATH)

# Backend default settings for chord duration and tempo
DEFAULT_CHORD_DURATION = 1  # 2 quarter notes (e.g., 2 seconds at 60 BPM)
DEFAULT_TEMPO_BPM = 120     # Tempo in beats per minute

@app.route("/")
def index():
    return render_template("index.html")

# Function to generate a chord as a WAV file
def generate_chord_audio(selected_key, selected_chord):
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

    # Generate MIDI and WAV filenames
    midi_filename = f"{AUDIO_DIR}/{selected_key}_{selected_chord}.mid"
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
