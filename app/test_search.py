from search_chords import search_chord_progression
import psycopg2

def test_search():
    # Define a test progression
    progression_to_search = ['C Minor', 'D Major', 'G Major', 'C Minor']
    progression_to_search = ["Dm7 alter b5","G7 add b9","Cm7","Cm7","E-m7","A-7","D-maj7","D-maj7"]
    # Connect to the database
    connection = psycopg2.connect("dbname=music user=xingchenchen password=yourpassword")

    try:
        # Call the search function
        results = search_chord_progression(progression_to_search, connection)

        # Output the results
        if results:
            print(f"Results for progression {progression_to_search}:")
            for result in results:
                print(f"- {result['song_name']} ({result['file_path']})")
        else:
            print(f"No matches found for progression {progression_to_search}.")
    finally:
        connection.close()

if __name__ == "__main__":
    test_search()
