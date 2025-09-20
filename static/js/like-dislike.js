function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-btn');
    const dislikeButtons = document.querySelectorAll('.dislike-btn');
    const csrftoken = getCookie('csrftoken');
    console.log('CSRF Token:', csrftoken);

    function sendRequest(button, url, action) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: `action=${action}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Находим обе кнопки в текущем card-footer
                const cardFooter = button.closest('.card-footer');
                const likeButton = cardFooter.querySelector('.like-btn');
                const dislikeButton = cardFooter.querySelector('.dislike-btn');
                const likeCount = likeButton.querySelector('.like-count');
                const dislikeCount = dislikeButton.querySelector('.dislike-count');
                
                // Обновляем оба счетчика
                if (likeCount) likeCount.textContent = data.like_count;
                if (dislikeCount) dislikeCount.textContent = data.dislike_count;

                // Обновляем data-action для обеих кнопок
                if (data.action === 'liked') {
                    likeButton.setAttribute('data-action', 'unlike');
                    dislikeButton.setAttribute('data-action', 'dislike');
                } else if (data.action === 'unliked') {
                    likeButton.setAttribute('data-action', 'like');
                    dislikeButton.setAttribute('data-action', 'dislike');
                } else if (data.action === 'disliked') {
                    dislikeButton.setAttribute('data-action', 'undislike');
                    likeButton.setAttribute('data-action', 'like');
                } else if (data.action === 'undisliked') {
                    dislikeButton.setAttribute('data-action', 'dislike');
                    likeButton.setAttribute('data-action', 'like');
                }
            } 
        })
        
    }

    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            const action = this.getAttribute('data-action');
            console.log('Sending request to:', url, 'with action:', action);
            sendRequest(this, url, action);
        });
    });

    dislikeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            const action = this.getAttribute('data-action');
            console.log('Sending request to:', url, 'with action:', action);
            sendRequest(this, url, action);
        });
    });
});