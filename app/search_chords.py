def search_chord_progression(progression, connection):
    """
    Searches the database for songs that match the given chord progression.

    Args:
        progression (list): A list of chords (e.g., ["C Minor", "F Minor"]).
        connection: PostgreSQL connection object.

    Returns:
        list: A list of matching songs with their file paths.
    """

    if not progression:
        print("Empty progression provided. Returning empty results.")
        return []

    cursor = connection.cursor()

    # Perform the SQL query to find exact or partial matches
    try:
        cursor.execute(
            """
            SELECT song_name, file_path
            FROM songs
            WHERE chord_progression @> %s OR chord_progression <@ %s
            """,
            (progression, progression)
        )
    except Exception as e:
        print(f"Error executing search query: {e}")
        return []

    # Fetch all results
    results = cursor.fetchall()

    if not results:
        print(f"No matches found for progression: {progression}")

    # Convert results into a list of dictionaries
    matches = [{"song_name": r[0], "file_path": r[1]} for r in results]

    return matches
