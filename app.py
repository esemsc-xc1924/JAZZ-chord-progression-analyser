from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Handle chord generation requests
@app.route("/generate_chord", methods=["POST"])
def generate_chord():
    data = request.get_json()
    key = data.get("key")
    chord = data.get("chord")

    # Placeholder response for now
    # In the future, generate a chord and return its MIDI/audio file path
    return jsonify({"status": "success", "key": key, "chord": chord, "audio_file": None})

if __name__ == "__main__":
    app.run(debug=True)
