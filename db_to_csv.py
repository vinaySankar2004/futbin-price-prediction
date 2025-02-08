import pandas as pd
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'futbin_archive'
}

connection = mysql.connector.connect(**db_config)
query = "SELECT * FROM joined_player_data"

output_csv = "joined_player_data.csv"

# Read and write in chunks
chunksize = 100000  # Number of rows per chunk
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    for i, chunk in enumerate(pd.read_sql_query(query, connection, chunksize=chunksize)):
        print(f"Processing chunk {i+1}")
        chunk.to_csv(f, index=False, header=(i == 0))  # Write header for the first chunk only
print("Export complete")
