import psycopg2

# Database connection details
conn = psycopg2.connect(
    dbname="VocalQuery", 
    user="postgres", 
    password="YOUR-POSTGRESQL-PASSWORD", 
    host="localhost", 
    port="5432"
)

# Create a cursor object
cur = conn.cursor()

# SQL commands to create the tables
create_lender_table = """
CREATE TABLE lender_signup (
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
"""


# Execute the SQL commands
cur.execute(create_lender_table)

# Commit the changes
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Tables created successfully.")
