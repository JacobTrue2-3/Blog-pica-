document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');
    const commentList = document.getElementById('comment-list');
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfInput ? csrfInput.value : null;
    const postId = commentForm ? commentForm.getAttribute('data-post-id') : null;
    const postSlug = commentForm ? commentForm.getAttribute('data-post-slug') : null;
    const parentCommentInput = document.getElementById('parent-comment-id');
    const replyPreview = document.getElementById('reply-preview');
    const replyPreviewContent = document.getElementById('reply-preview-content');
    const olderCommentsBtn = document.getElementById('older-comments-btn');

    console.log('postId:', postId, 'postSlug:', postSlug);

    if (!csrfToken && commentForm) {
        console.error('CSRF token not found.');
        alert('Ошибка: CSRF-токен не найден. Пожалуйста, обновите страницу.');
        return;
    }

    // === Функция для создания HTML комментария ===
    function createCommentHTML(commentData, isReply = false) {
    let max_steps = 5;
    let step = 20;
    let cycle_length = max_steps * 2;
    let cycle_level = commentData.level % cycle_length;
    let phase = (cycle_level >= max_steps) ? 1 : 0; // 0 для 0-4 (вправо), 1 для 5-9 (влево)
    let indent = phase === 0 ? cycle_level * step : (cycle_length - cycle_level) * step;

    return `
        <div class="comment mb-3" data-comment-id="${commentData.id}" data-text="${commentData.text.replace(/"/g, '&quot;')}" data-level="${commentData.level}" data-phase="${phase}">
            <div class="d-flex">
                <div class="comment-indent" style="width: ${indent}px;"></div>
                
                <div class="comment-content flex-grow-1 position-relative">
                    ${commentData.level > 0 ? '<div class="comment-connector"></div>' : ''}
                    
                    <div class="comment-card">
                        <div class="comment-header d-flex justify-content-between align-items-start mb-2">
                            <div class="d-flex align-items-center gap-2">
                                <strong class="comment-author text-primary">${commentData.author}</strong>
                                <small class="text-muted">
                                    ${commentData.created_at}
                                    ${commentData.is_edited ? '<span class="text-warning" title="Отредактирован">✎</span>' : ''}
                                </small>
                            </div>
                            
                            ${commentData.is_author ? `
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-light dropdown-toggle comment-actions" 
                                            type="button" data-bs-toggle="dropdown">
                                        <i class="bi bi-three-dots"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-end">
                                        <li>
                                            <a class="dropdown-item edit-comment" href="#" 
                                               data-comment-id="${commentData.id}" 
                                               data-url="/comments/${commentData.id}/edit/">
                                                <i class="bi bi-pencil me-2"></i>Редактировать
                                            </a>
                                        </li>
                                        <li>
                                            <a class="dropdown-item text-danger delete-comment" href="#" 
                                               data-comment-id="${commentData.id}" 
                                               data-url="/comments/${commentData.id}/delete/">
                                                <i class="bi bi-trash me-2"></i>Удалить
                                            </a>
                                        </li>
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="comment-text mb-3">
                            ${commentData.text.replace(/\n/g, '<br>')}
                        </div>
                        
                        <div class="comment-actions">
                            <button class="btn btn-sm btn-outline-primary reply-comment" 
                                    data-comment-id="${commentData.id}" 
                                    data-author="${commentData.author}">
                                <i class="bi bi-reply me-1"></i>Ответить
                            </button>
                        </div>
                    </div>
                    
                    ${commentData.replies && commentData.replies.length > 0 ? `
                        <div class="replies mt-3">
                            ${commentData.replies.map(reply => createCommentHTML(reply, true)).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

    // === Управление ветками комментариев ===
    function setupBranchManagement() {
        document.addEventListener('click', function(e) {
            // Сворачивание/разворачивание веток по двойному клику на заголовок
            if (e.target.classList.contains('comment-author') || 
                e.target.closest('.comment-author')) {
                if (e.detail === 2) { // Двойной клик
                    const commentCard = e.target.closest('.comment-card');
                    const replies = commentCard.parentElement.querySelector('.replies');
                    if (replies) {
                        replies.style.display = replies.style.display === 'none' ? 'block' : 'none';
                    }
                }
            }
        });
    }

    // Вызови при загрузке
    document.addEventListener('DOMContentLoaded', function() {
        setupBranchManagement();
    });
    // === Добавление нового комментария ===
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = commentForm.getAttribute('data-url');
            const text = commentForm.querySelector('textarea[name="text"]').value.trim();
            const parentId = parentCommentInput.value;
            
            if (!text) {
                alert('Комментарий не может быть пустым');
                return;
            }
            
            const formData = new URLSearchParams();
            formData.append('text', text);
            if (parentId) {
                formData.append('parent_id', parentId);
            }
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Не удалось добавить комментарий. Код ошибки: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const commentHtml = createCommentHTML(data.comment);
                    
                    if (data.comment.parent_id) {
                        // Находим родительский комментарий и добавляем ответ
                        const parentComment = document.querySelector(`.comment[data-comment-id="${data.comment.parent_id}"]`);
                        if (parentComment) {
                            const parentContent = parentComment.querySelector('.comment-content');
                            let repliesContainer = parentContent.querySelector('.replies');
                            if (!repliesContainer) {
                                repliesContainer = document.createElement('div');
                                repliesContainer.className = 'replies mt-3';
                                parentContent.appendChild(repliesContainer);
                            }
                            repliesContainer.insertAdjacentHTML('beforeend', commentHtml);
                        }
                    } else {
                        // Новый корневой комментарий добавляем в конец списка
                        if (commentList) {
                            commentList.insertAdjacentHTML('beforeend', commentHtml);
                            
                            // Если комментариев стало больше 5, скрываем самый старый
                            const allComments = commentList.querySelectorAll('.comment');
                            if (allComments.length > 5) {
                                // Скрываем самый первый комментарий (самый старый)
                                allComments[0].style.display = 'none';
                                
                                // Обновляем счетчик оставшихся комментариев
                                updateOlderCommentsCount(1);
                            }
                        } else {
                            const newCommentList = document.createElement('div');
                            newCommentList.id = 'comment-list';
                            newCommentList.innerHTML = commentHtml;
                            commentForm.parentElement.insertBefore(newCommentList, commentForm);
                        }
                        
                        // Прокручиваем к новому комментарию
                        const newComment = document.querySelector(`.comment[data-comment-id="${data.comment.id}"]`);
                        if (newComment) {
                            newComment.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                    }
                    
                    commentForm.reset();
                    cancelReply();
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

    // === Функция обновления счетчика старых комментариев ===
    function updateOlderCommentsCount(change) {
        const olderBtn = document.getElementById('older-comments-btn');
        if (!olderBtn) return;
        
        const match = olderBtn.textContent.match(/\((\d+)\)/);
        const currentCount = match ? parseInt(match[1]) : 0;
        const newCount = currentCount + change;
        
        if (newCount > 0) {
            olderBtn.innerHTML = `<i class="bi bi-arrow-up me-1"></i>Показать предыдущие комментарии (${newCount})`;
        } else {
            olderBtn.style.display = 'none';
        }
    }

    // === Загрузка предыдущих комментариев ===
    let olderCommentsOffset = 0;

    if (olderCommentsBtn) {
        olderCommentsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = `/posts/${postSlug}/more_comments/?offset=${olderCommentsOffset}`;
            console.log('Fetching older comments:', url);
            
            olderCommentsBtn.disabled = true;
            olderCommentsBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-1"></i>Загрузка...';
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Не удалось загрузить комментарии. Код ошибки: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Вставляем комментарии в начало списка
                    data.comments.forEach(commentData => {
                        const commentHtml = createCommentHTML(commentData);
                        commentList.insertAdjacentHTML('afterbegin', commentHtml);
                    });
                    
                    olderCommentsOffset = data.next_offset;
                    
                    // Обновляем кнопку или скрываем её
                    if (data.has_more) {
                        olderCommentsBtn.disabled = false;
                        olderCommentsBtn.innerHTML = `<i class="bi bi-arrow-up me-1"></i>Показать предыдущие комментарии (${data.older_comments_count})`;
                    } else {
                        olderCommentsBtn.style.display = 'none';
                    }
                } else {
                    alert(data.message || 'Произошла ошибка при загрузке комментариев');
                    olderCommentsBtn.disabled = false;
                    olderCommentsBtn.innerHTML = `<i class="bi bi-arrow-up me-1"></i>Показать предыдущие комментарии`;
                }
            })
            .catch(error => {
                console.error('Ошибка при загрузке комментариев:', error);
                alert(`Произошла ошибка при загрузке комментариев: ${error.message}`);
                olderCommentsBtn.disabled = false;
                olderCommentsBtn.innerHTML = `<i class="bi bi-arrow-up me-1"></i>Показать предыдущие комментарии`;
            });
        });
    }

    // === Ответ на комментарий ===
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-comment') || e.target.closest('.reply-comment')) {
            e.preventDefault();
            const button = e.target.classList.contains('reply-comment') ? e.target : e.target.closest('.reply-comment');
            const commentId = button.dataset.commentId;
            const author = button.dataset.author;
            
            parentCommentInput.value = commentId;
            replyPreviewContent.innerHTML = `Ответ пользователю <strong>${author}</strong>`;
            replyPreview.style.display = 'block';
            
            // Прокручиваем к форме
            commentForm.scrollIntoView({ behavior: 'smooth' });
            document.getElementById('comment-textarea').focus();
        }
    });

    // === Отмена ответа ===
    document.addEventListener('click', function(e) {
        if (e.target.id === 'cancel-reply') {
            cancelReply();
        }
    });

    function cancelReply() {
        parentCommentInput.value = '';
        replyPreview.style.display = 'none';
    }

    // === Обновление счётчика ===
    function updateCommentCount(change) {
        const header = document.querySelector('.card-header h2');
        if (!header) return;
        const match = header.textContent.match(/\d+/);
        const currentCount = match ? parseInt(match[0]) : 0;
        const newCount = currentCount + change;
        header.innerHTML = `<i class="bi bi-chat-square-text me-2"></i>Комментарии (${newCount})`;
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
                    const commentHtml = createCommentHTML(data.comment);
                    const commentDiv = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
                    commentDiv.innerHTML = commentHtml;
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
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
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
});