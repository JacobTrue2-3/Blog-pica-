// static/js/coment.js
document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');
    const commentList = document.getElementById('comment-list');
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfInput ? csrfInput.value : null;

    if (!csrfToken && commentForm) {
        console.error('CSRF token not found.');
        alert('Ошибка: CSRF-токен не найден. Пожалуйста, обновите страницу.');
        return;
    }

    // === Добавление нового комментария ===
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = commentForm.getAttribute('data-url');
            const text = commentForm.querySelector('textarea[name="text"]').value.trim();
            if (!text) {
                alert('Комментарий не может быть пустым');
                return;
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `text=${encodeURIComponent(text)}`
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Не удалось добавить комментарий. Код ошибки: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const commentHtml = `
                        <div class="comment mb-3" data-comment-id="${data.comment.id}" data-text="${data.comment.text.replace(/"/g, '&quot;')}">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>${data.comment.author}</strong>
                                    <small class="text-muted">${data.comment.created_at}${data.comment.is_edited ? ' (Редактирован)' : ''}</small>
                                    <p class="mb-1">${data.comment.text.replace(/\n/g, '<br>')}</p>
                                </div>
                                ${data.comment.is_author ? `
                                    <div class="dropdown">
                                        <button class="btn btn-sm btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                            <i class="bi bi-three-dots-vertical"></i>
                                        </button>
                                        <ul class="dropdown-menu">
                                            <li>
                                                <a class="dropdown-item edit-comment"
                                                   href="#"
                                                   data-comment-id="${data.comment.id}"
                                                   data-url="/comments/${data.comment.id}/edit/">Редактировать</a>
                                            </li>
                                            <li>
                                                <a class="dropdown-item text-danger delete-comment"
                                                   href="#"
                                                   data-comment-id="${data.comment.id}"
                                                   data-url="/comments/${data.comment.id}/delete/">Удалить</a>
                                            </li>
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                    if (commentList) {
                        commentList.insertAdjacentHTML('afterbegin', commentHtml);
                    } else {
                        const newCommentList = document.createElement('div');
                        newCommentList.id = 'comment-list';
                        newCommentList.innerHTML = commentHtml;
                        commentForm.parentElement.insertBefore(newCommentList, commentForm);
                    }
                    commentForm.reset();
                    updateCommentCount(1);
                } else {
                    alert(data.message || 'Не удалось добавить комментарий');
                }
            })
            .catch(error => {
                console.error('Ошибка при добавлении комментария:', error);
                alert(`Произошла ошибка при добавлении комментария: ${error.message}`);
            });
        });
    }

    // === Редактирование комментария ===
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('edit-comment')) {
            e.preventDefault();
            const commentId = e.target.dataset.commentId;
            const url = e.target.dataset.url;
            if (!url || url.includes('undefined')) {
                console.error('Недействительный URL для редактирования:', url);
                alert('Ошибка: Некорректный URL для редактирования');
                return;
            }
            const commentDiv = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
            if (!commentDiv) {
                console.error('Элемент комментария не найден для ID:', commentId);
                alert('Ошибка: Комментарий не найден');
                return;
            }
            const commentText = commentDiv.getAttribute('data-text') || '';

            console.log('Создание формы редактирования для комментария с ID:', commentId, 'URL:', url);
            const editFormHtml = `
                <form class="edit-comment-form" data-comment-id="${commentId}" data-url="${url}">
                    <div class="mb-3">
                        <textarea class="form-control" name="text" rows="3" required>${commentText}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary btn-sm me-2">Сохранить</button>
                    <button type="button" class="btn btn-secondary btn-sm cancel-edit">Отмена</button>
                </form>
            `;
            commentDiv.innerHTML = editFormHtml;
        }
    });

    // === Сохранение редактирования ===
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('edit-comment-form')) {
            e.preventDefault();
            const commentId = e.target.dataset.commentId;
            const url = e.target.dataset.url;
            if (!url || url.includes('undefined')) {
                console.error('Недействительный URL для сохранения редактирования:', url);
                alert('Ошибка: Некорректный URL для сохранения');
                return;
            }
            const text = e.target.querySelector('textarea[name="text"]').value.trim();
            if (!text) {
                alert('Комментарий не может быть пустым');
                return;
            }

            console.log('Отправка запроса на редактирование:', url);
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `text=${encodeURIComponent(text)}`
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Не удалось отредактировать комментарий. Код ошибки: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const commentDiv = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
                    commentDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${data.comment.author}</strong>
                                <small class="text-muted">${data.comment.created_at}${data.comment.is_edited ? ' (Редактирован)' : ''}</small>
                                <p class="mb-1">${data.comment.text.replace(/\n/g, '<br>')}</p>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li>
                                        <a class="dropdown-item edit-comment"
                                           href="#"
                                           data-comment-id="${commentId}"
                                           data-url="/comments/${commentId}/edit/">Редактировать</a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item text-danger delete-comment"
                                           href="#"
                                           data-comment-id="${commentId}"
                                           data-url="/comments/${commentId}/delete/">Удалить</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    `;
                    commentDiv.setAttribute('data-text', data.comment.text.replace(/"/g, '&quot;'));
                } else {
                    alert(data.message || 'Не удалось отредактировать комментарий');
                }
            })
            .catch(error => {
                console.error('Ошибка при редактировании комментария:', error);
                alert(`Произошла ошибка при редактировании комментария: ${error.message}`);
            });
        }
    });

    // === Отмена редактирования ===
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('cancel-edit')) {
            location.reload();
        }
    });

    // === Удаление комментария ===
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-comment')) {
            e.preventDefault();
            const commentId = e.target.dataset.commentId;
            const url = e.target.dataset.url;
            if (!url || url.includes('undefined')) {
                console.error('Недействительный URL для удаления:', url);
                alert('Ошибка: Некорректный URL для удаления');
                return;
            }
            if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
                fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Не удалось удалить комментарий. Код ошибки: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        document.querySelector(`.comment[data-comment-id="${commentId}"]`).remove();
                        updateCommentCount(-1);
                    } else {
                        alert(data.message || 'Не удалось удалить комментарий');
                    }
                })
                .catch(error => {
                    console.error('Ошибка при удалении комментария:', error);
                    alert(`Произошла ошибка при удалении комментария: ${error.message}`);
                });
            }
        }
    });

    // === Обновление счётчика ===
    function updateCommentCount(change) {
        const header = document.querySelector('.card-header h2');
        if (!header) return;
        const match = header.textContent.match(/\d+/);
        const currentCount = match ? parseInt(match[0]) : 0;
        const newCount = currentCount + change;
        header.innerHTML = `<i class="bi bi-chat-square-text me-2"></i>Комментарии (${newCount})`;
    }
});