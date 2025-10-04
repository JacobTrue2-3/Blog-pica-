document.addEventListener('DOMContentLoaded', function() {
    const favoriteButtons = document.querySelectorAll('.favorite-toggle');
    console.log('Found favorite buttons:', favoriteButtons.length);
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            console.log('Post ID:', postId);
            if (!postId) {
                alert('Ошибка: ID поста не найден');
                return;
            }
            const url = `/posts/${postId}/favorite/`; // Убрали /blog/
            console.log('Requesting URL:', url);
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({})
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.status === 'success') {
                    const icon = this.querySelector('i');
                    if (data.action === 'added') {
                        icon.classList.remove('text-muted', 'bi-star');
                        icon.classList.add('text-warning', 'bi-star-fill');
                    } else {
                        icon.classList.remove('text-warning', 'bi-star-fill');
                        icon.classList.add('text-muted', 'bi-star');
                    }
                } else {
                    console.error('Server error:', data.message);
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Ошибка при добавлении в избранное: ' + error.message);
            });
        });
    });

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
});