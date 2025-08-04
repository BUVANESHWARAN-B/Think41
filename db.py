import csv
import mysql.connector
from mysql.connector import Error

# --- Database Configuration ---
# Replace these with your actual database connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Buvi@2003',
    'database': 'ecommerce_dashboard'
}

# --- File Paths ---
# Replace these with the actual paths to your CSV files
USERS_CSV_PATH = 'users.csv'
ORDERS_CSV_PATH = 'orders.csv'

def insert_users_from_csv(cursor):
    """
    Reads the users.csv file and inserts the data into the 'users' table.
    Handles duplicate email errors by skipping the row.
    """
    # SQL query to check for the existence of a user by email
    check_user_sql = "SELECT user_id FROM users WHERE email = %s"
    
    try:
        with open(USERS_CSV_PATH, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            # Skip the header row
            next(csv_reader)
            
            sql = """INSERT INTO users 
                     (user_id, first_name, last_name, email, age, gender, state, 
                     street_address, postal_code, city, country, latitude, 
                     longitude, traffic_source, created_at)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            for row in csv_reader:
                # Handle potential empty strings for numeric/date fields
                row[4] = row[4] if row[4] else None  # age
                row[11] = row[11] if row[11] else None # latitude
                row[12] = row[12] if row[12] else None # longitude
                row[14] = row[14] if row[14] else None # created_at
                
                # Check for duplicate email before inserting to avoid errors
                cursor.execute(check_user_sql, (row[3],))
                if cursor.fetchone():
                    print(f"Warning: Skipping user with duplicate email: {row[3]}")
                    continue
                
                try:
                    cursor.execute(sql, tuple(row))
                except Error as e:
                    print(f"An error occurred while inserting user {row[0]}: {e}")
                
        print("User data loading complete.")
    except FileNotFoundError:
        print(f"Error: The file {USERS_CSV_PATH} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while inserting user data: {e}")

def insert_orders_from_csv(cursor):
    """
    Reads the orders.csv file and inserts the data into the 'orders' table.
    Skips orders where the user_id does not exist in the 'users' table.
    """
    # SQL query to check for the existence of a user by user_id
    check_user_sql = "SELECT user_id FROM users WHERE user_id = %s"

    try:
        with open(ORDERS_CSV_PATH, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            # Skip the header row
            next(csv_reader)
            
            sql = """INSERT INTO orders 
                     (order_id, user_id, status, created_at, returned_at, 
                     shipped_at, delivered_at, num_of_item)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            for row in csv_reader:
                order_id = row[0]
                user_id = row[1]
                
                # Check if the user_id exists in the users table before inserting the order
                cursor.execute(check_user_sql, (user_id,))
                if not cursor.fetchone():
                    print(f"Warning: Skipping order {order_id} because user_id {user_id} does not exist.")
                    continue

                status = row[2]
                created_at = row[4] if row[4] else None
                returned_at = row[5] if row[5] else None
                shipped_at = row[6] if row[6] else None
                delivered_at = row[7] if row[7] else None
                num_of_item = row[8] if row[8] else None
                
                data_tuple = (order_id, user_id, status, created_at, returned_at, shipped_at, delivered_at, num_of_item)
                
                try:
                    cursor.execute(sql, data_tuple)
                except Error as e:
                    print(f"An error occurred while inserting order {order_id}: {e}")

        print("Order data loading complete.")
    except FileNotFoundError:
        print(f"Error: The file {ORDERS_CSV_PATH} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while inserting order data: {e}")

def main():
    """
    Main function to connect to the database and run the data insertion.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        
        if conn.is_connected():
            print('Successfully connected to the database.')
            cursor = conn.cursor()
            
            insert_users_from_csv(cursor)
            insert_orders_from_csv(cursor)
            
            conn.commit()
            print("All data insertion committed successfully.")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    main()

