document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.querySelector("#userInput");
    const chatArea = document.querySelector("#chatArea");
    const botUser = "Resume Bot"
    const username = "You"

    userInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            const messageContent = e.target.value.trim();
            if (messageContent.length === 0) return;

            // Display user message
            addMessageToChat(username, messageContent);

            // Send data to backend
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageContent })
            })
            .then(response => response.json())
            .then(data => {
                // Display bot typing indicator
                addTypingIndicator();

                setTimeout(() => {
                    removeTypingIndicator();
                    typeText("Bot", data.message);
                }, 500); // Adjust the delay as needed
            })
            .catch(error => {
                console.error('Error:', error);
                addMessageToChat(botUser, "Sorry, something went wrong. Please try again.");
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

    function addTypingIndicator() {
        const typingElement = document.createElement("div");
        typingElement.classList.add("message");
        typingElement.id = "typingIndicator";
        typingElement.innerHTML = `<div class="username">Bot: </div><div class="messageContent"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
        chatArea.appendChild(typingElement);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingElement = document.getElementById("typingIndicator");
        if (typingElement) {
            typingElement.remove();
        }
    }

    function typeText(username, text) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        const usernameDiv = document.createElement("div");
        usernameDiv.classList.add("username");
        usernameDiv.textContent = `${username}: `;
        const messageContentDiv = document.createElement("div");
        messageContentDiv.classList.add("messageContent");
        messageElement.appendChild(usernameDiv);
        messageElement.appendChild(messageContentDiv);
        chatArea.appendChild(messageElement);
        chatArea.scrollTop = chatArea.scrollHeight;

        let index = 0;
        const speed = 30;

        function type() {
            if (index < text.length) {
                messageContentDiv.innerHTML += text.charAt(index);
                index++;
                chatArea.scrollTop = chatArea.scrollHeight;
                setTimeout(type, speed);
            }
        }

        type();
    }
});
