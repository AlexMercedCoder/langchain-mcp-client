document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = input.value.trim();

        if (!message) return;

        appendMessage(message, "user");
        input.value = "";
        input.disabled = true;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.response) {
                appendMessage(data.response, "agent");
            } else if (data.error) {
                appendMessage(`Error: ${data.error}`, "agent");
            }
        } catch (err) {
            appendMessage("Failed to connect to server.", "agent");
        }

        input.disabled = false;
        input.focus();
    });

    function appendMessage(text, role) {
        const messageEl = document.createElement("div");
        messageEl.classList.add("message", role);
        messageEl.textContent = text;
        chatWindow.appendChild(messageEl);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
