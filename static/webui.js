document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const chatWindow = document.getElementById("chat-window");
    const resetButton = document.getElementById("reset-chat");

    // Hook: Submit message
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
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.response) {
                appendMessage(data.response, "agent");
            } else if (data.error) {
                appendMessage(`Error: ${data.error}`, "agent");
            }
        } catch (err) {
            appendMessage("Could not reach the server.", "agent");
        }

        input.disabled = false;
        input.focus();
    });

    // Hook: Reset chat history
    resetButton.addEventListener("click", async () => {
        try {
            const response = await fetch("/reset", {
                method: "POST",
            });

            const result = await response.json();
            chatWindow.innerHTML = "";  // Clear messages visually
            appendMessage("Chat history has been cleared.", "agent");
        } catch (err) {
            appendMessage("Failed to reset chat history.", "agent");
        }
    });

    // Append message to chat window
    function appendMessage(text, role) {
        const messageEl = document.createElement("div");
        messageEl.classList.add("message", role);

        const bubble = document.createElement("div");
        bubble.classList.add("bubble");
        bubble.innerHTML = DOMPurify.sanitize(marked.parse(text));  // Markdown rendering

        messageEl.appendChild(bubble);
        chatWindow.appendChild(messageEl);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
