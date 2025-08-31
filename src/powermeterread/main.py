from dotenv import load_dotenv
import os 
import shutil
import pandas as pd
import pyodbc
import glob


load_dotenv() # Load environment variables from .env file

# Ensure all required environment variables are set
csv_location = os.getenv("CSV_LOCATION")
if not csv_location:
    raise ValueError("CSV_LOCATION environment variable is not set.")

csv_archive = os.getenv("CSV_ARCHIVE_LOCATION")
if not csv_archive:
    raise ValueError("CSV_ARCHIVE_LOCATION environment variable is not set.")

sql_server = os.getenv("SQL_SERVER_NAME")
if not sql_server:
    raise ValueError("SQL_SERVER_NAME environment variable is not set.")

database = os.getenv("SQL_DATABASE_NAME")
if not database:
    raise ValueError("SQL_DATABASE_NAME environment variable is not set.")

db_user = os.getenv("SQL_USER_NAME")
if not db_user:
    raise ValueError("SQL_USER_NAME environment variable is not set.")

db_password = os.getenv("SQL_USER_PASSWORD")
if not db_password:
    raise ValueError("SQL_USER_PASSWORD environment variable is not set.")

raw_table = os.getenv("SQL_RAW_TABLE_NAME")
if not raw_table:
    raise ValueError("SQL_RAW_TABLE_NAME environment variable is not set.")


csv_files = glob.glob(os.path.join(csv_location, "*.CSV"))

print(csv_files)

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={sql_server};"
    f"DATABASE={database};"
    f"UID={db_user};"
    f"PWD={db_password};"
    "TrustServerCertificate=yes;"
    "Encrypt=yes;"
)

total_inserted = 0  # Track total rows inserted across all files

cursor = conn.cursor()

for file_path in csv_files:
    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path)

    table_name = raw_table
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['?'] * len(df.columns))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    inserted_count = 0  # Track rows inserted from this file

    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_sql, row)
        inserted_count += 1

    conn.commit()
    print(f"Inserted {inserted_count} rows from {os.path.basename(file_path)}")
    total_inserted += inserted_count

    # Move processed file to archive
    shutil.move(file_path, os.path.join(csv_archive, os.path.basename(file_path)))


cursor.execute(f"SELECT COUNT(*) FROM {raw_table}")
row_count = cursor.fetchone()[0]
print(f"Total rows inserted into {raw_table} during this run: {total_inserted}")

# Execute SP to merge data into the main table
cursor.execute("exec sp_PowerUsageMergeToMain")
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
