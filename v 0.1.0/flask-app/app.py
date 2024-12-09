from flask import Flask, request, render_template, jsonify, session
import base64
import time
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Connect to PostgreSQL database

def get_db_connection():
    # Read secrets from files
    with open('/run/secrets/db_username', 'r') as f:
        username = f.read().strip()
    with open('/run/secrets/db_password', 'r') as f:
        password = f.read().strip()
    with open('/run/secrets/db_name', 'r') as f:
        dbname = f.read().strip()

    conn = psycopg2.connect(
        host="db",  # Name of the database service
        database=dbname,
        user=username,
        password=password
    )
    return conn


# Encryption function using base64 and salt
def encrypt_input(input_string):
    salt = "miraculin"
    combined_string = input_string + salt
    encrypted = base64.b64encode(combined_string.encode()).decode()
    return encrypted

# Function to insert encrypted string into the database
def insert_encrypted_string(encrypted_string):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO xor_table (xor_value) VALUES (%s)", (encrypted_string,))
    conn.commit()
    cur.close()
    conn.close()

# Function to retrieve last 100 encrypted strings from DB
def get_latest_encrypted_strings():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, xor_value FROM xor_table ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Function to decode the encrypted string
def decode_string(encrypted_string):
    try:
        decoded_bytes = base64.b64decode(encrypted_string)
        return decoded_bytes.decode().replace("miraculin", "")  # Remove salt before returning
    except Exception as e:
        return None

# Function to delete an encrypted string
def delete_encrypted_string(encrypted_string):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM xor_table WHERE xor_value = %s", (encrypted_string,))
    conn.commit()
    cur.close()
    conn.close()

# Delay mechanism
def check_time_limit(session_key):
    last_action_time = session.get(session_key)
    current_time = time.time()
    if last_action_time and current_time - last_action_time < 15:
        return False
    session[session_key] = current_time
    return True

# Routes
@app.route('/')
def index():
    entries = get_latest_encrypted_strings()
    return render_template('index.html', entries=entries)

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    if not check_time_limit('last_encrypt_time'):
        return jsonify({'success': False, 'error': 'Please wait 15 seconds before trying again.'})

    user_input = request.form['user_input']
    if len(user_input) <= 3:
        encrypted_string = encrypt_input(user_input)
        insert_encrypted_string(encrypted_string)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Input too long'})

@app.route('/decode', methods=['POST'])
def decode_route():
    if not check_time_limit('last_decode_time'):
        return jsonify({'success': False, 'error': 'Please wait 15 seconds before trying again.'})

    encrypted_string = request.form['hash_value']
    decoded_value = decode_string(encrypted_string)
    if decoded_value:
        return jsonify({'success': True, 'decoded': decoded_value})
    return jsonify({'success': False, 'error': 'Failed to decode'})

@app.route('/delete', methods=['POST'])
def delete_route():
    if not check_time_limit('last_delete_time'):
        return jsonify({'success': False, 'error': 'Please wait 15 seconds before trying again.'})

    encrypted_string = request.form['hash_value']
    delete_encrypted_string(encrypted_string)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
