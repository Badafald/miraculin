from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

ENCRYPTION_SERVICE_URL = 'http://encryption_service:5001'
STORAGE_SERVICE_URL = 'http://storage_service:5002'

@app.route('/')
@limiter.limit("5 per minute")  # Limit to 5 requests per minute to load the main page
def index():
    response = requests.get(f"{STORAGE_SERVICE_URL}/retrieve")
    entries = response.json().get('entries', [])
    return render_template('index.html', entries=entries)

@app.route('/encrypt', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 encryption requests per minute
def encrypt_route():
    user_input = request.json.get('user_input', '')
    encryption_response = requests.post(f"{ENCRYPTION_SERVICE_URL}/encrypt", json={'user_input': user_input})
    if encryption_response.json().get('success'):
        encrypted_string = encryption_response.json().get('encrypted')
        store_response = requests.post(f"{STORAGE_SERVICE_URL}/store", json={'encrypted_string': encrypted_string})
        return store_response.json()
    return jsonify(encryption_response.json())

@app.route('/decode', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 decryption requests per minute
def decode_route():
    encrypted_string = request.json.get('encrypted_string', '')
    decode_response = requests.post(f"{ENCRYPTION_SERVICE_URL}/decrypt", json={'encrypted_string': encrypted_string})
    return decode_response.json()

@app.route('/delete', methods=['POST'])
@limiter.limit("10 per minute")  # Limit to 10 delete requests per minute
def delete_route():
    encrypted_string = request.json.get('encrypted_string', '')
    delete_response = requests.post(f"{STORAGE_SERVICE_URL}/delete", json={'encrypted_string': encrypted_string})
    return delete_response.json()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
