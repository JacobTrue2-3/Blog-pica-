function toggleTags(postId) {
    const tagsWrapper = document.getElementById(`tags-${postId}`);
    const hiddenTags = tagsWrapper.querySelector('.hidden-tags');
    const toggleButton = tagsWrapper.parentElement.querySelector('.tags-toggle');
    
    if (hiddenTags.style.display === 'none') {
        hiddenTags.style.display = 'inline';
        tagsWrapper.style.maxHeight = 'none';
        toggleButton.textContent = '▲ Свернуть';
    } else {
        hiddenTags.style.display = 'none';
        tagsWrapper.style.maxHeight = '32px';
        const count = toggleButton.dataset.count;
        toggleButton.textContent = `+${count} ещё`;
    }
}