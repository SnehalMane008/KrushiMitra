import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )

def setup_database():
    # Connect to MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("Creating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS agri_store")
        cursor.execute("USE agri_store")
        
        # Drop tables if they exist to start fresh
        print("Recreating users table...")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table with email field
        cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            role ENUM('admin', 'staff') NOT NULL
        )
        """)
        
        # Add admin and sample user
        print("Adding user accounts...")
        cursor.execute("""
        INSERT INTO users (username, password, role) 
        VALUES 
            ('admin', 'admin123', 'admin'),
            ('user', 'user123', 'staff')
        """)
        
        # Create other tables if they don't exist
        cursor.execute("SHOW TABLES LIKE 'customers'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(15),
                address TEXT
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'suppliers'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE suppliers (
                supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(15),
                address TEXT
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'products'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                quantity INT,
                price DECIMAL(10,2),
                supplier_id INT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'product_supplier'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE product_supplier (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                supplier_id INT,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'sales'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY,
                sale_date DATE,
                customer_id INT,
                total_amount DECIMAL(10,2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'sales_items'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE sales_items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                sale_id INT,
                product_id INT,
                quantity INT,
                price DECIMAL(10,2),
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
            )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'deliveries'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE deliveries (
                delivery_id INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id INT,
                delivery_date DATE,
                quantity INT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
            )
            """)
        
        conn.commit()
        print("Database setup complete!")
        
        # Print current users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"Users in database: {len(users)}")
        for user in users:
            print(f"User: {user[1]}, Role: {user[3]}")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database() 