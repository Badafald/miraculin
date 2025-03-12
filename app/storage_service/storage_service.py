from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USERNAME"]
    db_password = os.environ["DB_PASSWORD"]
    
    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432")
    )

@app.route('/store', methods=['POST'])
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
def retrieve_encrypted_strings():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, xor_value FROM xor_table ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'entries': rows})

@app.route('/delete', methods=['POST'])
def delete_encrypted_string():
    encrypted_string = request.json.get('encrypted_string', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM xor_table WHERE xor_value = %s", (encrypted_string,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})

# Health and readiness endpoints
@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

@app.route('/ready', methods=['GET'])
def ready():
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except:
        return "Not Ready", 503

if __name__ == '__main__':
    app.run(port=5002, debug=True)
