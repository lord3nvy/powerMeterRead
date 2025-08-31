from powermeterread.emailDownload import EmailAttachmentDownloader
from dotenv import load_dotenv
import os 
import shutil
import pandas as pd
import pyodbc
import glob


load_dotenv() # Load environment variables from .env file

# Gather all required environment variables in a dictionary
required_env_vars = {
    "CSV_LOCATION": os.getenv("CSV_LOCATION"),
    "CSV_ARCHIVE_LOCATION": os.getenv("CSV_ARCHIVE_LOCATION"),
    "SQL_SERVER_NAME": os.getenv("SQL_SERVER_NAME"),
    "SQL_DATABASE_NAME": os.getenv("SQL_DATABASE_NAME"),
    "SQL_USER_NAME": os.getenv("SQL_USER_NAME"),
    "SQL_USER_PASSWORD": os.getenv("SQL_USER_PASSWORD"),
    "SQL_RAW_TABLE_NAME": os.getenv("SQL_RAW_TABLE_NAME"),
    "EMAIL": os.getenv("EMAIL"),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
    "IMAP_SERVER": os.getenv("IMAP_SERVER"),
    "SENDER_EMAIL": os.getenv("SENDER_EMAIL")
}

# Find any missing variables
missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"The following environment variables are not set: {', '.join(missing_vars)}")

# Unpack variables for use
csv_location = required_env_vars["CSV_LOCATION"]
csv_archive = required_env_vars["CSV_ARCHIVE_LOCATION"]
sql_server = required_env_vars["SQL_SERVER_NAME"]
database = required_env_vars["SQL_DATABASE_NAME"]
db_user = required_env_vars["SQL_USER_NAME"]
db_password = required_env_vars["SQL_USER_PASSWORD"]
raw_table = required_env_vars["SQL_RAW_TABLE_NAME"]
email = required_env_vars["EMAIL"]
email_password = required_env_vars["EMAIL_PASSWORD"]
imap_server = required_env_vars["IMAP_SERVER"]
sender_email = required_env_vars["SENDER_EMAIL"]

# Initialize the email attachment downloader
downloader = EmailAttachmentDownloader(
    email_address = email,
    password = email_password,
    imap_server = imap_server,
    sender = sender_email,
    save_dir = csv_location
)

# Connect to the email server and download attachments
print("Connecting to email server and downloading attachments...")
downloader.connect()
downloader.download_attachments()
downloader.logout()

# Find all CSV files in the save directory
csv_files = glob.glob(os.path.join(csv_location, "*.CSV"))
if not csv_files:
    print("No CSV files found to process.")
    exit(0)

# Connect to the SQL Server database
print("Connecting to SQL Server...")
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

print("Data processing complete. All files processed and archived.")