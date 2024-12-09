from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
import os

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

def get_db_connection():
    # Read secrets from the Docker secrets path
    with open('/run/secrets/db_name', 'r') as f:
        db_name = f.read().strip()
    with open('/run/secrets/db_username', 'r') as f:
        db_user = f.read().strip()
    with open('/run/secrets/db_password', 'r') as f:
        db_password = f.read().strip()

    # Establish the database connection
    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host='db',  # This should match the service name in Docker Compose
        port=5432
    )


@app.route('/store', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 store requests per minute per IP
def store_encrypted_string():
    encrypted_string = request.json.get('encrypted_string', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO xor_table (xor_value) VALUES (%s) RETURNING id", (encrypted_string,))
    conn.commit()
    new_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({'success': True, 'id': new_id})

@app.route('/retrieve', methods=['GET'])
@limiter.limit("5 per minute")  # Limit to 5 retrieval requests per minute per IP
def retrieve_encrypted_strings():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, xor_value FROM xor_table ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'entries': rows})

@app.route('/delete', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 delete requests per minute per IP
def delete_encrypted_string():
    encrypted_string = request.json.get('encrypted_string', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM xor_table WHERE xor_value = %s", (encrypted_string,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5002, debug=True)