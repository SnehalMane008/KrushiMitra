import mysql.connector
import os

def setup_database():
    """
    Set up the database and tables based on the SQL script
    """
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root'
    }
    
    conn = None
    cursor = None
    
    try:
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Read SQL script
        script_path = os.path.join(os.path.dirname(__file__), 'db_setup.sql')
        print(f"Reading SQL script from {script_path}...")
        
        with open(script_path, 'r') as f:
            sql_script = f.read()
        
        # Split SQL statements and execute them one by one
        print("Executing SQL statements...")
        # Enable multi-statement execution
        for statement in sql_script.split(';'):
            # Skip empty statements
            if statement.strip():
                try:
                    cursor.execute(statement)
                    conn.commit()
                except mysql.connector.Error as err:
                    print(f"Error executing statement: {err}")
                    print(f"Statement: {statement}")
        
        print("Database setup complete!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database() 