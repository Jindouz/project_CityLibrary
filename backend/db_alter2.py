import sqlite3

def add_customers_id_column(database_path):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Disable foreign key constraint enforcement temporarily
        cursor.execute("PRAGMA foreign_keys=off;")

        # Begin transaction
        cursor.execute("BEGIN TRANSACTION;")

        # Add a new column named 'CustomersID' to the 'users' table
        cursor.execute("ALTER TABLE users ADD COLUMN CustomersID INTEGER;")

        # Define the foreign key constraint for the new column
        cursor.execute("""
            CREATE TABLE users_new(Id INTEGER PRIMARY KEY, 
                                   username VARCHAR(50), 
                                   password TEXT, 
                                   is_admin BOOLEAN, 
                                   CustomersID INTEGER, 
                                   FOREIGN KEY(CustomersID) REFERENCES Customers(Id));
            INSERT INTO users_new(Id, username, password, is_admin) 
                SELECT Id, username, password, is_admin FROM users;
            DROP TABLE users;
            ALTER TABLE users_new RENAME TO users;
        """)

        # Re-enable foreign key constraint enforcement
        cursor.execute("PRAGMA foreign_keys=on;")

        # End transaction
        cursor.execute("COMMIT;")

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

        print("Column 'CustomersID' added successfully.")

    except sqlite3.Error as e:
        print("Error:", e)

# Specify the path to your SQLite database
database_path = 'instance/library.db'  # Replace with your actual database path

# Call the function to add the new column
add_customers_id_column(database_path)