document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('chatForm'); 
    const chatbox = document.getElementById('chatBody'); 

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const messageInput = document.getElementById('userMessage'); 
        const userMessage = messageInput.value;

        chatbox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.reply}</p>`;
            messageInput.value = '';
        })
        .catch(error => {
            chatbox.innerHTML += `<p><strong>Error:</strong> ${error}</p>`;
        });
    });
});
