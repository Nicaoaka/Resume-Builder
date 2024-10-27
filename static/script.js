document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.querySelector("#userInput");
    const chatArea = document.querySelector("#chatArea");

    userInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            const messageContent = e.target.value.trim();
            if (messageContent.length === 0) return;

            // Display user message
            addMessageToChat("You", messageContent);

            // Send data to backend
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageContent })
            })
            .then(response => response.json())
            .then(data => {
                addMessageToChat("Bot", data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessageToChat("Bot", "Sorry, something went wrong. Please try again.");
            });

            e.target.value = "";
        }
    });

    function addMessageToChat(username, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.innerHTML = `<div class="username">${username}: </div><div class="messageContent">${message}</div>`;
        chatArea.appendChild(messageElement);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
});
