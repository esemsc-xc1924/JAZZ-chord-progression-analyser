import mido
import pygame
import time


# Function to create a MIDI file for a chord
def create_midi_file(midi_notes, filename="chord.mid", duration=1.0, tempo=120):
    """
    Creates a MIDI file with the given chord notes.
    :param midi_notes: List of MIDI note numbers
    :param filename: Name of the MIDI file to save
    :param duration: Duration of the chord in seconds
    :param tempo: Tempo in beats per minute
    """
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Convert tempo to microseconds per beat
    microseconds_per_beat = mido.bpm2tempo(tempo)
    track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat))

    # Add note-on messages
    for note in midi_notes:
        track.append(mido.Message('note_on', note=note, velocity=64, time=0))

    # Add a delay for the chord duration
    delay = int(duration * 480)  # Assuming 480 ticks per beat
    track.append(mido.Message('note_off', note=midi_notes[0], velocity=64, time=delay))

    # Add note-off messages
    for note in midi_notes[1:]:
        track.append(mido.Message('note_off', note=note, velocity=64, time=0))

    # Save the MIDI file
    mid.save(filename)
    print(f"MIDI file saved as {filename}")


# Function to play a MIDI file using pygame
def play_midi_file(filename):
    """
    Plays the given MIDI file using pygame.
    :param filename: Name of the MIDI file to play
    """
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)


# Example: Create and play a C7 altered chord
base_chord = [60, 64, 67, 70]  # C7 (C, E, G, Bb)
alterations = [61, 66]  # b9 and #11 (Db and F#)
midi_chord = base_chord + alterations

# Create and play the MIDI file
create_midi_file(midi_chord, filename="altered_chord.mid", duration=2.0, tempo=120)
play_midi_file("altered_chord.mid")
