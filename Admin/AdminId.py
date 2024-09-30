import sqlite3

# Path to the database
from config import db_path

# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object
cursor = conn.cursor()

# Create the Admins table
create_table_query = '''
CREATE TABLE IF NOT EXISTS Admins (
    AdminId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
'''

# Execute the query to create the table
cursor.execute(create_table_query)

# Insert demo data into the Admins table
insert_data_query = '''
INSERT INTO Admins (AdminId,name, email, password) 
VALUES 
    ('Admin001','John Doe', 'johndoe@example.com', 'password123');
   
'''

cursor.execute(insert_data_query)


conn.commit()


cursor.execute('SELECT * FROM Admins')
rows = cursor.fetchall()

for row in rows:
    print(row)

# Close the connection
conn.close()
