// Add to static/js/main.js
document.querySelector('select[name="availability"]').addEventListener('change', function() {
    const indicator = document.querySelector('.status-indicator');
    indicator.textContent = this.options[this.selectedIndex].text;
    indicator.classList.remove('available', 'away');
    indicator.classList.add(this.value);
});