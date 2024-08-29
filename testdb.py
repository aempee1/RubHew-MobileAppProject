import psycopg2


try:
    connection = psycopg2.connect("postgresql://admin:admin1234@localhost/dbrubhew")
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")