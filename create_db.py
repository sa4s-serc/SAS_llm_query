import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("temperature_data.db")
cursor = conn.cursor()

# Create table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS temperature_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        temperature FLOAT
    )
"""
)

# Generate fake data
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 1, 1)
current_date = start_date

while current_date < end_date:
    # Generate a random temperature between -10°C and 40°C
    temperature = round(random.uniform(-10, 40), 1)

    # Insert the data into the database
    cursor.execute(
        """
        INSERT INTO temperature_readings (timestamp, temperature)
        VALUES (?, ?)
    """,
        (current_date.isoformat(), temperature),
    )

    # Move to the next hour
    current_date += timedelta(hours=1)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'temperature_data.db' has been created with fake temperature data.")
