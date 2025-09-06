document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".date-field").forEach(el => {
        const dateString = el.getAttribute('data-date') || el.textContent.trim();
        try {
            const date = new Date(dateString);
            if (isNaN(date)) {
                throw new Error("Невалидная дата");
            }
            el.textContent = date.toLocaleString('ru-RU', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            console.error('Ошибка форматирования даты:', error, 'Дата:', dateString);
            el.textContent = 'Невалидная дата';
        }
    });
});