import psycopg2

def test_connection():
    try:
        # Replace "yourpassword" with the actual password
        connection = psycopg2.connect("dbname=music user=xingchenchen password=yourpassword")
        print("Connection successful!")
    except Exception as e:
        print("Connection failed.")
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    test_connection()
