import base64
from flask import Flask, jsonify, request, session, render_template
from flask_cors import CORS
import os
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import pooling
from datetime import timedelta
import re
from werkzeug.security import generate_password_hash

# Securely use environment variables for DB connection
# --- DB CONFIG -------------------------------------------------------
database_url = os.getenv('JAWSDB_MARIA_URL') # JawsDB URL from Heroku
if database_url:
    url = urlparse(database_url)
    db_config = {
        'host': url.hostname,
        'user': url.username,
        'password': url.password,
        'database': url.path[1:],
        'port': url.port or 3306,
        # NEW: SSL & sane timeouts
        'ssl_ca': os.getenv('MYSQL_SSL_CA', '/app/certs/rds-ca-2019-root.pem'),
        'connection_timeout': 5,
        'pool_name': 'mypool',
        'pool_size': int(os.getenv('MYSQL_POOL_SIZE', 3)),
        'pool_reset_session': True,
    }

    print(f"Using JawsDB configuration with host: {url.hostname}")
else:
    # Local fallback for development/testing
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'clubhub_db'),
        'pool_name': 'mypool',
        'pool_size': 5
    }
    print(f"Using local configuration with host: {db_config['host']}")
# ---------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'some_super_secret_key_here')  # Use environment variable

# Create connection pool
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
    print("Successfully created connection pool")
except mysql.connector.Error as err:
    print(f"Failed to create connection pool: {err}")
    connection_pool = None

# Allow both your custom domains (www and non-www); adjust as needed
CORS(
    app,
    resources={r"/*": {"origins": [
        "https://club-hub-app.com",
        "https://www.club-hub-app.com"
    ]}},
    supports_credentials=True
)

app.permanent_session_lifetime = timedelta(minutes=20)

def get_db_connection():
    """
    Borrow a connection from the pool (or open a direct one in local dev),
    then make sure the socket is still alive.  If MySQL closed it while
    idle, ping(reconnect=True) transparently re-opens it.
    """
    try:
        # 1️⃣ grab a connection
        conn = connection_pool.get_connection() if connection_pool \
               else mysql.connector.connect(**db_config)

        # 2️⃣ verify / revive it (two tries, 1-second pause between)
        conn.ping(reconnect=True, attempts=2, delay=1)

        return conn
    except mysql.connector.Error as err:
        print(f"[DB] connection error: {err}")
        return None


def close_db_connection(connection):
    """
    Helper function to safely close database connections.
    """
    if connection and connection.is_connected():
        connection.close()

# -------------------------
# Existing CRUD Endpoints
# -------------------------
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/about_page')
def about_page():
    return render_template('about.html')

@app.route('/contact_page')
def contact_page():
    return render_template('home.html')

@app.route('/explore_clubs_page')
def explore_clubs_page():
    return render_template('explore_clubs.html')

@app.route('/people_page')
def people_page():
    return render_template('people.html')

@app.route('/account_page')
def account_page():
    return render_template('account.html')

@app.route('/create_account_page')      
def create_account_page():
    return render_template('create_account.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    cursor.close()
    close_db_connection(connection)
    return jsonify(users), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        close_db_connection(connection)
        return jsonify({"error": "User not found"}), 404

    if user.get('profile_image'):
        encoded = base64.b64encode(user['profile_image']).decode('utf-8')
        user['profile_image'] = f"data:image/jpeg;base64,{encoded}"

    club_cursor = connection.cursor(dictionary=True)
    club_cursor.execute("""
        SELECT c.id, c.name
        FROM clubs c
        JOIN user_clubs uc ON c.id = uc.club_id
        WHERE uc.user_id = %s
    """, (user_id,))
    club_rows = club_cursor.fetchall()
    club_cursor.close()
    cursor.close()
    close_db_connection(connection)

    if club_rows:
        user['clubs'] = [{"id": row['id'], "name": row['name']} for row in club_rows]
    else:
        user['clubs'] = []

    return jsonify(user), 200


@app.route('/api/users', methods=['POST'])
def add_user():
    """
    Creates a new user (sign-up).
    Expects JSON with username, email, password, firstname, lastname
    """
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')

    if not username or not email or not password or not firstname or not lastname:
        return jsonify({"error": "All fields are required"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
    cursor.execute(check_query, (username, email))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        close_db_connection(connection)
        return jsonify({"error": "Username or email already in use"}), 400

    insert_query = """
        INSERT INTO users (username, email, password, firstname, lastname)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (username, email, password, firstname, lastname))
    connection.commit()
    user_id = cursor.lastrowid

    cursor.close()
    close_db_connection(connection)

    return jsonify({
        "id": user_id,
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname
    }), 201

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes a user by user_id.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
    connection.commit()
    cursor.close()
    close_db_connection(connection)

    return jsonify({"message": "User deleted successfully"}), 200


@app.route('/api/login', methods=['POST'])
def login():
    """
    Handles user login. Expects JSON with username, password.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    login_query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(login_query, (username, password))
    user = cursor.fetchone()

    cursor.close()
    close_db_connection(connection)

    if user:
        session.permanent = True
        session['user_id'] = user['id']
        if user.get('profile_image'):
            encoded = base64.b64encode(user['profile_image']).decode('utf-8')
            user['profile_image'] = f"data:image/jpeg;base64,{encoded}"

        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Clears session (logs the user out).
    """
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    """
    Returns the currently logged-in user's info, including:
    - base64-encoded profile_image (if present)
    - a clubs list (if using user_clubs join table)
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"user": None}), 200

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    # 1) Get user row
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    user = cursor.fetchone()

    if user and user.get('profile_image'):
        # Convert BLOB to base64
        encoded = base64.b64encode(user['profile_image']).decode('utf-8')
        user['profile_image'] = f"data:image/jpeg;base64,{encoded}"

    # 2) Get user's clubs
    club_cursor = connection.cursor(dictionary=True)
    club_cursor.execute("""
        SELECT c.id, c.name
        FROM clubs c
        JOIN user_clubs uc ON c.id = uc.club_id
        WHERE uc.user_id = %s
    """, (user_id,))
    club_rows = club_cursor.fetchall()
    club_cursor.close()

    if club_rows:
        user['clubs'] = [{"id": row['id'], "name": row['name']} for row in club_rows]
    else:
        user['clubs'] = []

    cursor.close()
    close_db_connection(connection)

    return jsonify({"user": user}), 200


@app.route('/api/clubs/<int:club_id>', methods=['GET'])
def get_club(club_id):
    """
    Returns a single club by ID.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clubs WHERE id = %s;", (club_id,))
    club = cursor.fetchone()
    cursor.close()
    close_db_connection(connection)

    if club:
        return jsonify(club), 200
    else:
        return jsonify({"error": "Club not found"}), 404

@app.route('/api/clubs', methods=['GET'])
def get_all_clubs():
    """
    Returns all clubs.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clubs;")
    clubs = cursor.fetchall()
    cursor.close()
    close_db_connection(connection)

    return jsonify(clubs), 200

@app.route('/api/users/upload_picture', methods=['POST'])
def profile_image():
    """
    Updates the currently logged-in user's profile image (BLOB in DB),
    then returns the base64-encoded image URI in JSON.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    if 'profilePicture' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['profilePicture']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Read raw bytes
    file_bytes = file.read()

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor()
    update_query = "UPDATE users SET profile_image = %s WHERE id = %s"
    cursor.execute(update_query, (file_bytes, user_id))
    connection.commit()
    cursor.close()
    close_db_connection(connection)

    # Detect file extension for data URI
    extension = file.filename.rsplit('.', 1)[-1].lower()
    if extension == 'png':
        mime_type = 'image/png'
    elif extension in ['jpg', 'jpeg']:
        mime_type = 'image/jpeg'
    else:
        mime_type = 'image/jpeg'

    # Convert file bytes to base64
    encoded_str = base64.b64encode(file_bytes).decode('utf-8')
    data_uri = f"data:{mime_type};base64,{encoded_str}"

    return jsonify({"profile_image": data_uri}), 200

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """
    GET /api/users/search?q=Jane
    Returns a list of users whose firstname OR lastname OR 
    the combination 'firstname lastname' matches the query.
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([]), 200

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    search_str = f"%{query}%"
    search_query = """
        SELECT id, username, email, firstname, lastname, profile_image
        FROM users
        WHERE firstname LIKE %s
           OR lastname LIKE %s
           OR CONCAT(firstname, ' ', lastname) LIKE %s
    """
    cursor.execute(search_query, (search_str, search_str, search_str))
    results = cursor.fetchall()

    # Base64 encode profile_image
    for user in results:
        if user.get('profile_image'):
            user['profile_image'] = (
                "data:image/jpeg;base64,"
                + base64.b64encode(user['profile_image']).decode('utf-8')
            )

    cursor.close()
    close_db_connection(connection)

    return jsonify(results), 200

@app.route('/api/clubs/by_college/<int:college_id>', methods=['GET'])
def get_clubs_by_college(college_id):
    """
    Returns all clubs associated with a given college_id.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT c.id, c.name
        FROM clubs c
        JOIN college_clubs cc ON c.id = cc.club
        WHERE cc.college = %s
    """
    cursor.execute(query, (college_id,))
    clubs = cursor.fetchall()
    cursor.close()
    close_db_connection(connection)

    return jsonify(clubs), 200

@app.route('/api/test-db', methods=['GET'])
def test_db():
    """
    Test endpoint to verify database connection and basic operations
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({
            "status": "error",
            "message": "Failed to connect to database",
            "config": {
                "host": db_config['host'],
                "database": db_config['database'],
                "user": db_config['user']
            }
        }), 500

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Test 1: Basic connection
        cursor.execute("SELECT 1")
        test1 = cursor.fetchone()
        
        # Test 2: Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table = cursor.fetchone()
        
        # Test 3: Count users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()
        
        cursor.close()
        close_db_connection(connection)
        
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "tests": {
                "basic_connection": test1,
                "users_table_exists": bool(users_table),
                "user_count": user_count['count'] if user_count else 0
            }
        }), 200
        
    except mysql.connector.Error as err:
        cursor.close()
        close_db_connection(connection)
        return jsonify({
            "status": "error",
            "message": f"Database operation failed: {str(err)}"
        }), 500

@app.route('/api/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Check if username exists in database
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    close_db_connection(connection)
    
    return jsonify({'exists': result is not None})

@app.route('/api/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if email exists in database
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    result = cursor.fetchone()
    cursor.close()
    close_db_connection(connection)
    
    return jsonify({'exists': result is not None})

@app.route('/api/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'firstname', 'lastname']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength (minimum 8 characters, at least one number and one letter)
    if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", data['password']):
        return jsonify({'error': 'Password must be at least 8 characters long and contain at least one letter and one number'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Hash the password
        hashed_password = generate_password_hash(data['password'])
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (username, email, password, firstname, lastname)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            data['username'],
            data['email'],
            hashed_password,
            data['firstname'],
            data['lastname']
        ))
        
        connection.commit()
        cursor.close()
        close_db_connection(connection)
        
        return jsonify({'message': 'Account created successfully'}), 201
        
    except Exception as e:
        print(f"Error creating account: {e}")  # Add logging
        connection.rollback()
        cursor.close()
        close_db_connection(connection)
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
