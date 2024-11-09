import mysql.connector
from mysql.connector import errorcode
import bcrypt

# Database connection configuration
config = {
    'user': 'root',        # Your MySQL username
    'password': 'root', # Your MySQL password
    'port':'1207',      # Port
    'host': '127.0.0.1',    # Your MySQL server (localhost for local development)
}

# Database and table creation
DB_NAME = 'elax_pos'

TABLES = {
    'Employee': '''
        CREATE TABLE IF NOT EXISTS Employee (
            employee_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(100) NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('Active', 'Inactive') DEFAULT 'Active'
        )
    ''',
    'Inventory': '''
        CREATE TABLE IF NOT EXISTS Inventory (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            quantity INT DEFAULT 0,
            price DECIMAL(10, 2) NOT NULL,
            barcode VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''',
    'Sales': '''
        CREATE TABLE IF NOT EXISTS Sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT,
            total_amount DECIMAL(10, 2) NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
        )
    ''',
    'Sales_Items': '''
        CREATE TABLE IF NOT EXISTS Sales_Items (
            sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
            sale_id INT,
            item_id INT,
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES Sales(sale_id),
            FOREIGN KEY (item_id) REFERENCES Inventory(item_id)
        )
    ''',
    'Purchase': '''
        CREATE TABLE IF NOT EXISTS Purchase (
            purchase_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT,
            quantity INT NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            supplier VARCHAR(255),
            cost_price DECIMAL(10, 2),
            FOREIGN KEY (item_id) REFERENCES Inventory(item_id)
        )
    ''',
    'Report': '''
        CREATE TABLE IF NOT EXISTS Report (
            report_id INT AUTO_INCREMENT PRIMARY KEY,
            report_type VARCHAR(100) NOT NULL,
            data TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'Login_Logs': '''
        CREATE TABLE IF NOT EXISTS Login_Logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
        )
    '''
}

def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database {DB_NAME} created successfully.")
    except mysql.connector.Error as err:
        print(f"Failed to create database {DB_NAME}: {err}")

def setup_tables(cursor):
    cursor.execute(f"USE {DB_NAME}")
    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table {table_name}...")
            cursor.execute(ddl)
            print(f"Table {table_name} created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Table {table_name} already exists.")
            else:
                print(f"Error creating table {table_name}: {err}")


def insert_default_accounts(cursor):
    # Default users
    default_users = [
        {"name": "admin", "role": "Admin", "username": "admin", "password": "admin123"},
        {
            "name": "waiter",
            "role": "Waiter",
            "username": "waiter",
            "password": "waiter123",
        },
    ]

    for user in default_users:
        # Check if the user already exists
        cursor.execute(
            "SELECT * FROM Employee WHERE username = %s", (user["username"],)
        )
        if cursor.fetchone() is None:
            # Hash password
            hashed_password = bcrypt.hashpw(
                user["password"].encode("utf-8"), bcrypt.gensalt()
            )
            # Insert user
            cursor.execute(
                "INSERT INTO Employee (name, role, username, password) VALUES (%s, %s, %s, %s)",
                (user["name"], user["role"], user["username"], hashed_password),
            )
            print(f"Inserted default user: {user['username']}")
        else:
            print(f"User {user['username']} already exists.")


def main():
    try:
        # Connect to MySQL server
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create the database if it doesn't exist
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        if not cursor.fetchone():
            create_database(cursor)

        # Set up tables within the database
        setup_tables(cursor)

        cursor.close()
        cnx.close()
        print("Database setup completed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()

    # Existing database setup code...
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        # Database and table setup
        cursor.execute(f"USE {DB_NAME}")
        setup_tables(cursor)
        insert_default_accounts(cursor)
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if "cnx" in locals() and cnx.is_connected():
            cnx.close()

if __name__ == "__main__":
    main()
