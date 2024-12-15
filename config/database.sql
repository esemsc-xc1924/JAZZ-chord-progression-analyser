-- Database Schema for the Chord Progression Database

-- Create the songs table
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,              -- Unique song identifier
    song_name VARCHAR(255) NOT NULL,    -- Name of the song
    file_path VARCHAR(255) NOT NULL,    -- Path to the .musicxml file
    chord_progression TEXT[] NOT NULL,  -- Array of chords (e.g., ["C I", "G V"])
    created_at TIMESTAMP DEFAULT NOW()  -- Timestamp for record creation
);

-- Index on chord_progression for efficient searching
CREATE INDEX chord_progression_idx ON songs USING GIN (chord_progression);
