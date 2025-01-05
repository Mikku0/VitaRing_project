
const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle("show");
  });
}

// Upload Image
const photoInput = document.querySelector("#avatar");
const photoPreview = document.querySelector("#preview-avatar");
if (photoInput)
  photoInput.onchange = () => {
    const [file] = photoInput.files;
    if (file) {
      photoPreview.src = URL.createObjectURL(file);
    }
  };

// Scroll to Bottom
const conversationThread = document.querySelector(".room__box");
if (conversationThread) conversationThread.scrollTop = conversationThread.scrollHeight;

document.addEventListener('DOMContentLoaded', function() {
    const moreButton = document.getElementById('show-button');
    const topicList = document.querySelector('.topics__list__transition');

    topicList.classList.remove('hide');

    moreButton.addEventListener('click', function(event) {
        event.preventDefault();

        topicList.classList.toggle('hide');

        if (topicList.classList.contains('hide')) {
            moreButton.innerHTML = 'Show <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><title>chevron-down</title><path d="M16 21l-13-13h-3l16 16 16-16h-3l-13 13z"></path></svg>';
        } else {
            moreButton.innerHTML = 'Hide <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><title>chevron-up</title><path d="M16 11l13 13h3l-16-16-16 16h3l13-13z"></path></svg>';
        }
    });
});

document.getElementById("send_button").addEventListener("click", function() {
    let message = document.getElementById("user_input").value;
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // Pobierz token CSRF

    fetch('/chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,  // Dodaj token CSRF do nagłówka
        },
        body: 'message=' + encodeURIComponent(message),
    })
    .then(response => response.json())
    .then(data => {
        let chatlog = document.getElementById("chatlog");

        // Dodaj wiadomość użytkownika
        let userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        chatlog.appendChild(userMessage);

        // Dodaj odpowiedź chatbota
        let botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        chatlog.appendChild(botMessage);

        document.getElementById("user_input").value = '';  // Wyczyść pole po wysłaniu
        chatlog.scrollTop = chatlog.scrollHeight;  // Przewiń do dołu
    });
});

document.getElementById("user_input").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("send_button").click();  // Wyślij wiadomość po Enter
    }
});
