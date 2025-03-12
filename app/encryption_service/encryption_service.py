from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

def encrypt_string(input_string):
    salt = "miraculin"
    combined_string = input_string + salt
    encrypted = base64.b64encode(combined_string.encode()).decode()
    return encrypted

def decrypt_string(encrypted_string):
    try:
        decoded_bytes = base64.b64decode(encrypted_string)
        return decoded_bytes.decode().replace("miraculin", "")
    except Exception:
        return None

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    user_input = request.json.get('user_input', '')
    if len(user_input) > 3:
        return jsonify({'success': False, 'error': 'Input too long'}), 400
    encrypted_string = encrypt_string(user_input)
    return jsonify({'success': True, 'encrypted': encrypted_string})

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    encrypted_string = request.json.get('encrypted_string', '')
    decrypted_value = decrypt_string(encrypted_string)
    if decrypted_value:
        return jsonify({'success': True, 'decrypted': decrypted_value})
    return jsonify({'success': False, 'error': 'Failed to decrypt'}), 400

# Health and readiness endpoints
@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

@app.route('/ready', methods=['GET'])
def ready():
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
