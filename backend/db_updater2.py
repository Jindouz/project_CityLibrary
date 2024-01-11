import sqlite3

def update_password_data_type(database_path):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Execute the SQL command to change the data type
        cursor.execute("PRAGMA foreign_keys=off;")
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("CREATE TABLE Users_backup AS SELECT * FROM Users;")
        cursor.execute("DROP TABLE Users;")
        cursor.execute("CREATE TABLE Users (Id INTEGER PRIMARY KEY, Username VARCHAR(50) UNIQUE NOT NULL, Password TEXT NOT NULL, is_admin BOOLEAN, CustomerID INTEGER, FOREIGN KEY(CustomerID) REFERENCES Customer(Id));")
        cursor.execute("INSERT INTO Users (Id, Username, Password, is_admin) SELECT Id, Username, Password, is_admin FROM Users_backup;")
        cursor.execute("DROP TABLE Users_backup;")
        cursor.execute("COMMIT;")

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

        print("Data type updated successfully.")

    except sqlite3.Error as e:
        print("Error:", e)


# Specify the path to your SQLite database
database_path = 'instance/library.db'  # Replace with your actual database path

# Call the function to update the data type
update_password_data_type(database_path)