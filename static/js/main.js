console.log('=== MAIN.JS START ===');
console.log('Token:', !!localStorage.getItem('access'));
console.log('Path:', window.location.pathname);

(function() {
    var token = localStorage.getItem('access');
    var publicPages = ['/login/', '/register/', '/'];
    var currentPath = window.location.pathname;

    // Редирект если нет токена
    if (!token && !publicPages.includes(currentPath)) {
        window.location.href = '/login/';
        return;
    }

    // Кнопки
    var navButtons = document.getElementById('navButtons');
    console.log('navButtons found:', !!navButtons);

    if (navButtons) {
        if (token) {
            navButtons.innerHTML = '<a href="/profile/" class="btn btn-secondary">Профиль</a> <button class="btn btn-primary" onclick="logout()">Выйти</button>';
        } else {
            navButtons.innerHTML = '<a href="/login/" class="btn btn-secondary">Войти</a> <a href="/register/" class="btn btn-primary">Регистрация</a>';
        }
    }

    // Навигация
    var navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.style.display = token ? 'flex' : 'none';
    }

    console.log('=== MAIN.JS END ===');
})();

function logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login/';
}