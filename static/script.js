const button = document.querySelector(".send-button");
const textarea = document.querySelector("textarea");
const chatbox = document.querySelector(".ChatBox");

button.addEventListener("click", function () {

        let message = textarea.value;

        if (message.trim() === "")
            return;

        let newMsg = document.createElement("div");
        newMsg.classList.add("message");
        newMsg.textContent = message;

        chatbox.appendChild(newMsg);
        textarea.value = "";
    });

textarea.addEventListener("keypress", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        button.click();
    }
});