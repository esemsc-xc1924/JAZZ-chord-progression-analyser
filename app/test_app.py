from flask import Flask, request, jsonify
import psycopg2
from search_chords import search_chord_progression

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Music Chord Search API. Use the `/search_chords` endpoint to search for chord progressions."

# Database connection setup
def get_db_connection():
    return psycopg2.connect("dbname=music user=xingchenchen password=yourpassword")

@app.route('/search_chords', methods=['POST'])
def search_chords():
    data = request.get_json()
    progression = data.get('progression', [])

    if not progression:
        return jsonify({"error": "No progression provided"}), 400

    connection = get_db_connection()
    try:
        results = search_chord_progression(progression, connection)
        return jsonify({"matches": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
