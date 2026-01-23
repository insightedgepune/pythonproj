from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import hashlib
import os
from datetime import datetime
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'database': os.environ.get('DB_NAME', 'login_db'),
    'user': os.environ.get('DB_USER', 'login_user'),
    'password': os.environ.get('DB_PASSWORD', 'user_password'),
    'auth_plugin': 'mysql_native_password'
}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def setup_database():
    """Setup database and tables if they don't exist"""
    print("Setting up database...")
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (id INT AUTO_INCREMENT PRIMARY KEY,
                              username VARCHAR(50) UNIQUE NOT NULL,
                              password VARCHAR(255) NOT NULL,
                              email VARCHAR(100),
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              last_login TIMESTAMP NULL)''')
            
            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Hash the password for admin user
                hashed_password = hash_password("admin123")
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                              ("admin", hashed_password, "admin@example.com"))
                print("Created default admin user: admin / admin123")
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Database setup completed!")
            
        except Error as e:
            print(f"Error during setup: {e}")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = create_database_connection()
        if not connection:
            flash('Cannot connect to database', 'error')
            return render_template('login.html')
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                user_id, stored_password = user
                if hash_password(password) == stored_password:
                    # Update last login
                    cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", 
                                  (datetime.now(), user_id))
                    connection.commit()
                    
                    session['user_id'] = user_id
                    session['username'] = username
                    flash(f'Welcome, {username}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password', 'error')
            else:
                flash('User not found', 'error')
                
        except Error as e:
            flash(f'Database error: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        errors = []
        if len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        connection = create_database_connection()
        if not connection:
            flash('Cannot connect to database', 'error')
            return render_template('register.html')
        
        try:
            cursor = connection.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            # Insert new user
            hashed_password = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                          (username, hashed_password, email))
            connection.commit()
            
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
            
        except Error as e:
            flash(f'Database error: {e}', 'error')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = create_database_connection()
    users = []
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY id")
            users = cursor.fetchall()
            cursor.close()
        except Error as e:
            flash(f'Error loading users: {e}', 'error')
        connection.close()
    
    return render_template('dashboard.html', username=session['username'], users=users)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Setup database
    setup_database()
    
    # Run Flask app
    print("Starting Flask application on http://0.0.0.0:5000")
    print("Access the application at: http://localhost:5000")
    print("Default credentials: admin / admin123")
    app.run(host='0.0.0.0', port=5000, debug=True)