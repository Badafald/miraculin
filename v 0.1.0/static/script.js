function showSuccess(button) {
    button.classList.add('success');
    setTimeout(() => {
        button.classList.remove('success');
    }, 2000); // Glow for 2 seconds
}

function handleError(button, errorMsg) {
    const errorSpan = document.getElementById('error-message-' + button.id);
    errorSpan.textContent = errorMsg;
    errorSpan.style.display = 'inline'; // Show error message
}

function hideError(button) {
    const errorSpan = document.getElementById('error-message-' + button.id);
    errorSpan.textContent = '';
    errorSpan.style.display = 'none'; // Hide error message
}

function encryptInput() {
    const userInput = document.getElementById('user_input').value;
    const button = document.getElementById('encrypt-button');
    hideError(button);

    fetch('/encrypt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `user_input=${userInput}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(button);
            window.location.reload(); // Reload to show new entry
        } else {
            handleError(button, data.error);
        }
    });
}

function decodeInput() {
    const hashValue = document.getElementById('selected_hash').value;
    const button = document.getElementById('decode-button');
    hideError(button);

    fetch('/decode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `hash_value=${hashValue}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('decoded_output').innerText = 'Decoded value: ' + data.decoded;
            showSuccess(button);
        } else {
            handleError(button, data.error);
        }
    });
}

function deleteInput() {
    const hashValue = document.getElementById('selected_hash').value;
    const button = document.getElementById('delete-button');
    hideError(button);

    if (hashValue === '') {
        handleError(button, 'Please select an encrypted string to delete.');
        return;
    }

    fetch('/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `hash_value=${hashValue}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(button);
            window.location.reload(); // Reload to show updated list
        } else {
            handleError(button, data.error);
        }
    });
}