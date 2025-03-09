import base64
from flask import Flask, jsonify, request, session, render_template
from flask_cors import CORS
import os
from urllib.parse import urlparse
import mysql.connector
from datetime import timedelta

# Securely use environment variables for DB connection
database_url = os.environ.get('JAWSDB_MARIA_URL')

if database_url:
    url = urlparse(database_url)
    db_config = {
        'host': url.hostname,
        'user': url.username,
        'password': url.password,
        'database': url.path[1:],  # Removes leading '/'
        'port': url.port or 3306
    }
else:
    # Local fallback for development/testing
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'mydbpassword123!!!',
        'database': 'clubhub_db'
    }

app = Flask(__name__)
app.secret_key = "some_super_secret_key_here"  # Use an environment variable in production

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
    Helper function to connect to MySQL. 
    Returns a connection or None on failure.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

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

@app.route('/explore_clubs')
def explore_clubs_page():
    return render_template('explore_clubs.html')

@app.route('/people')
def people_page():
    return render_template('people.html')


@app.route('/api/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
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
        connection.close()
        return jsonify({"error": "User not found"}), 404

    # If you have a profile_image column, do base64 encoding here:
    if user.get('profile_image'):
        encoded = base64.b64encode(user['profile_image']).decode('utf-8')
        user['profile_image'] = f"data:image/jpeg;base64,{encoded}"

    # Now get clubs
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
    connection.close()

    # Convert list of dicts into a simpler structure
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
        # Username or Email already exists
        cursor.close()
        connection.close()
        return jsonify({"error": "Username or email already in use"}), 400

    insert_query = """
        INSERT INTO users (username, email, password, firstname, lastname)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (username, email, password, firstname, lastname))
    connection.commit()
    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

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
    connection.close()

    return jsonify({"message": "User deleted successfully"}), 200

# -------------------------
# Session-based Login
# -------------------------
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
    connection.close()

    if user:
        session.permanent = True
        # Save to session
        session['user_id'] = user['id']
        # If user has a BLOB in profile_image, base64-encode it for JSON
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
    connection.close()

    return jsonify({"user": user}), 200

# -------------------------
# Club Endpoints
# -------------------------
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
    connection.close()

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
    connection.close()

    return jsonify(clubs), 200

# -------------------------
# Picture Upload
# -------------------------
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
    connection.close()

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
    connection.close()

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
    connection.close()

    return jsonify(clubs), 200

if __name__ == '__main__':
    app.run(debug=True)
