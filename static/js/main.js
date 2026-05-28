console.log('=== MAIN.JS START ===');
console.log('Token:', !!localStorage.getItem('access'));
console.log('Path:', window.location.pathname);

(function() {
    var token = localStorage.getItem('access');
    var publicPages = ['/login/', '/register/', '/'];
    var currentPath = window.location.pathname;

    if (!token && !publicPages.includes(currentPath)) {
        window.location.href = '/login/';
        return;
    }

    var navButtons = document.getElementById('navButtons');
    if (navButtons) {
        if (token) {
            navButtons.innerHTML = '<a href="/profile/" class="btn btn-secondary">Профиль</a> <button class="btn btn-primary" onclick="logout()">Выйти</button>';
        } else {
            navButtons.innerHTML = '<a href="/login/" class="btn btn-secondary">Войти</a> <a href="/register/" class="btn btn-primary">Регистрация</a>';
        }
    }

    var navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.style.display = token ? 'flex' : 'none';
    }

    // Счётчик уведомлений
    if (token) {
        updateNotifBadge();
        setInterval(updateNotifBadge, 30000);
    }

    console.log('=== MAIN.JS END ===');
})();

function updateNotifBadge() {
    var T = localStorage.getItem('access');
    if (!T) return;
    fetch('http://localhost:8000/api/tasks/notifications/', {
        headers: { 'Authorization': 'Bearer ' + T }
    }).then(function(r) { return r.json(); }).then(function(d) {
        var unread = (d.results || []).filter(function(n) { return !n.is_read; }).length;
        var badge = document.getElementById('notif-badge');
        if (badge) {
            badge.textContent = unread;
            badge.style.display = unread > 0 ? 'inline' : 'none';
        }
    }).catch(function() {});
}

function logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login/';
}