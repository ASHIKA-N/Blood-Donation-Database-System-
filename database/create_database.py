import sqlite3
import os

# Step 1: Define paths
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "blood_donation_system.db")  # ✅ New name
SCHEMA_PATH = os.path.join(BASE_DIR, "blood_donation.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed.sql")

# Step 2: Create database and apply schema
print("🔧 Setting up database...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 3: Execute schema file (CREATE TABLE)
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

# Step 4: Execute seed file (INSERT data)
with open(SEED_PATH, "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

# Step 5: Commit and close
conn.commit()
conn.close()

print("✅ Database 'blood_donation_system.db' created and seeded successfully!")
