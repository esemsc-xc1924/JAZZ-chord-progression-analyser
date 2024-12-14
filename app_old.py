from flask import Flask, render_template, request, jsonify, send_from_directory
from music21 import key, chord, stream, midi
from midi2audio import FluidSynth
import os

app = Flask(__name__)

# Directory to store generated audio files
AUDIO_DIR = "static/sounds"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Path to the SoundFont file
SOUNDFONT_PATH = "/Users/xingchenchen/Desktop/JAZZ-chord-progression-analyser/GeneralUserGSv1.471.sf2"
# Initialize FluidSynth with the SoundFont
fs = FluidSynth(SOUNDFONT_PATH)

# Serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Function to generate a chord as a WAV file
def generate_chord_audio(selected_key, selected_chord):
    # Map chord types to scale degrees
    roman_to_scale = {
        "I": [1, 3, 5],
        "ii": [2, 4, 6],
        "iii": [3, 5, 7],
        "IV": [4, 6, 1],
        "V": [5, 7, 2],
        "vi": [6, 1, 3],
        "vii°": [7, 2, 4],
    }

    # Create a key object
    music_key = key.Key(selected_key)

    # Get the chord pitches
    scale_degrees = roman_to_scale[selected_chord]
    pitches = [music_key.pitchFromDegree(degree) for degree in scale_degrees]

    # Create a chord object
    music_chord = chord.Chord(pitches)

    # Create a music21 Stream
    s = stream.Stream()
    s.append(music_chord)

    # Generate MIDI filename
    midi_filename = f"{AUDIO_DIR}/{selected_key}_{selected_chord}.mid"
    wav_filename = midi_filename.replace(".mid", ".wav")

    # Write MIDI file
    mf = midi.translate.music21ObjectToMidiFile(s)
    mf.open(midi_filename, "wb")
    mf.write()
    mf.close()

    # Convert MIDI to WAV using FluidSynth
    fs.midi_to_audio(midi_filename, wav_filename)

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
