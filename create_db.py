import sqlite3

conn = sqlite3.connect("sql_env.db")
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary REAL
);

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    budget REAL
);

INSERT INTO departments VALUES (1, 'Engineering', 500000);
INSERT INTO departments VALUES (2, 'Marketing', 200000);
INSERT INTO departments VALUES (3, 'HR', 150000);

INSERT INTO employees VALUES (1, 'Alice', 'Engineering', 95000);
INSERT INTO employees VALUES (2, 'Bob', 'Engineering', 88000);
INSERT INTO employees VALUES (3, 'Carol', 'Marketing', 72000);
INSERT INTO employees VALUES (4, 'Dave', 'HR', 65000);
INSERT INTO employees VALUES (5, 'Eve', 'Marketing', 78000);
""")

conn.commit()
conn.close()
print("✓ sql_env.db created successfully")