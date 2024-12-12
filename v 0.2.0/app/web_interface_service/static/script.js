function toggleButtonSuccess(buttonId, success) {
    const button = document.getElementById(buttonId);
    if (success) {
        button.classList.add("success");
        setTimeout(() => button.classList.remove("success"), 2000); // Revert after 2 seconds
    }
}

function encryptInput() {
    const userInput = document.getElementById("user_input").value;
    fetch('/encrypt', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_input: userInput})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            toggleButtonSuccess("encrypt-button", true);
            location.reload(); // Refresh to show the updated list
        } else {
            alert(data.error);
        }
    });
}

function decodeInput() {
    const selectedHash = document.getElementById("selected_hash").value;
    fetch('/decode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({encrypted_string: selectedHash})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            toggleButtonSuccess("decode-button", true);
            document.getElementById("decoded_output").innerText = `Decoded: ${data.decrypted}`;
        } else {
            alert(data.error);
        }
    });
}

function deleteInput() {
    const selectedHash = document.getElementById("selected_hash").value;
    fetch('/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({encrypted_string: selectedHash})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            toggleButtonSuccess("delete-button", true);
            location.reload(); // Refresh to remove the deleted item
        } else {
            alert(data.error);
        }
    });
}
