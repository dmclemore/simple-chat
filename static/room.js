const socket = io.connect("http://" + document.domain + ":" + location.port);

$(() => {
    // On page load, trigger socket join event.
    socket.emit("join", {
        room: $("#roomId").val(),
    });

    // Add event listeners
    socket.on("renderMessage", handleRenderMessage);
    $("#chat-form").on("submit", handleChatMessage);
    $("#chat-submit").on("click", handleChatMessage);
});

function handleRenderMessage(data) {
    // If there is a valid chat message, get the HTML and append it to the chat

    if (typeof data.username !== "undefined" && data.message !== "") {
        const newMessage = $(generateChatMessageHTML(data));
        $("#chat-all-messages").append(newMessage);
        $("#chat-all-messages").scrollTop($("#chat-all-messages").height());
    }
}

function generateChatMessageHTML(message) {
    // Create the HTML for a given message

    return `
        <p>
            <span class="font-weight-bold text-danger">${message.username}: </span>${message.message}
        </p>
    `;
}

function handleChatMessage(evt) {
    // Emit the message to the server socket and reset the form

    evt.preventDefault();
    const username = $("#chat-user").val();
    const message = $("#chat-message").val();
    if (message == "" || username == "") return;
    socket.emit("send_chat", {
        username: username,
        message: message,
    });
    $("#chat-form").trigger("reset");
}
