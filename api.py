import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- Database Configuration ---
# Replace these with your actual database connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Buvi@2003',
    'database': 'ecommerce_dashboard'
}

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# --- Flask Application Setup ---
app = Flask(__name__)
# Enable CORS for all routes, allowing frontend applications to access the API
CORS(app)

# --- API Endpoints ---

@app.route('/api/customers', methods=['GET'])
def list_customers():
    """
    API endpoint to list all customers with pagination.
    Accepts 'page' and 'per_page' query parameters.
    Example: /api/customers?page=1&per_page=10
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Query to get total number of customers for pagination metadata
        count_query = "SELECT COUNT(*) FROM users"
        cursor.execute(count_query)
        total_count = cursor.fetchone()['COUNT(*)']

        # Query to get paginated list of customers
        customers_query = """
            SELECT user_id, first_name, last_name, email, created_at 
            FROM users 
            LIMIT %s OFFSET %s
        """
        cursor.execute(customers_query, (per_page, offset))
        customers = cursor.fetchall()
        
        response = {
            "customers": customers,
            "total_count": total_count,
            "page": page,
            "per_page": per_page
        }
        return jsonify(response), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    """
    API endpoint to get details for a specific customer, including their order count.
    Handles 'customer not found' errors.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Query to get customer details and their order count using a LEFT JOIN
        query = """
            SELECT u.user_id, u.first_name, u.last_name, u.email, u.age, u.gender, 
                   u.city, u.country, u.created_at, COUNT(o.order_id) AS order_count
            FROM users u
            LEFT JOIN orders o ON u.user_id = o.user_id
            WHERE u.user_id = %s
            GROUP BY u.user_id
        """
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer:
            return jsonify(customer), 200
        else:
            return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Run the Flask Application ---
if __name__ == '__main__':
    # You can change the host and port as needed
    app.run(host='0.0.0.0', port=5000, debug=True)

