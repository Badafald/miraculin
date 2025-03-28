from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

ENCRYPTION_SERVICE_URL = os.environ.get('ENCRYPTION_SERVICE_URL', 'http://encryption-service:5001')
STORAGE_SERVICE_URL = os.environ.get('STORAGE_SERVICE_URL', 'http://storage-service:5002')

@app.route('/')
def index():
    response = requests.get(f"{STORAGE_SERVICE_URL}/retrieve")
    entries = response.json().get('entries', [])
    return render_template('index.html', entries=entries)

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    user_input = request.json.get('user_input', '')
    encryption_response = requests.post(f"{ENCRYPTION_SERVICE_URL}/encrypt", json={'user_input': user_input})
    if encryption_response.json().get('success'):
        encrypted_string = encryption_response.json().get('encrypted')
        store_response = requests.post(f"{STORAGE_SERVICE_URL}/store", json={'encrypted_string': encrypted_string})
        return store_response.json()
    return jsonify(encryption_response.json())

@app.route('/decode', methods=['POST'])
def decode_route():
    encrypted_string = request.json.get('encrypted_string', '')
    decode_response = requests.post(f"{ENCRYPTION_SERVICE_URL}/decrypt", json={'encrypted_string': encrypted_string})
    return decode_response.json()

@app.route('/delete', methods=['POST'])
def delete_route():
    encrypted_string = request.json.get('encrypted_string', '')
    delete_response = requests.post(f"{STORAGE_SERVICE_URL}/delete", json={'encrypted_string': encrypted_string})
    return delete_response.json()


@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

@app.route('/ready', methods=['GET'])
def ready():

    try:
        r = requests.get(f"{STORAGE_SERVICE_URL}/retrieve", timeout=2)
        if r.status_code == 200:
            return "OK", 200
        else:
            return "Can't reach storage service", 503
    except Exception:
        return "Can't reach storage service", 503

if __name__ == '__main__':
    app.run(port=5000, debug=True)
