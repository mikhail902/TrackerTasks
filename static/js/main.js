(function() {
    const token = localStorage.getItem('access');
    const publicPages = ['/login/', '/register/', '/'];
    const currentPath = window.location.pathname;

    if (!token && !publicPages.includes(currentPath)) {
        window.location.href = '/login/';
        return;
    }

    if (token && publicPages.includes(currentPath) && currentPath !== '/') {
        window.location.href = '/home/';
        return;
    }

    const navContent = document.getElementById('navContent');
    if (token) {
        navContent.innerHTML = `
            <ul class="navbar-nav flex-grow-1">
                <li class="nav-item"><a class="nav-link" href="/home/">Обзор</a></li>
                <li class="nav-item"><a class="nav-link" href="/dashboard/">Дашборд</a></li>
                <li class="nav-item"><a class="nav-link" href="/projects/">Проекты</a></li>
                <li class="nav-item"><a class="nav-link" href="/tasks/">Задачи</a></li>
                <li class="nav-item"><a class="nav-link" href="/notifications/">Уведомления</a></li>
            </ul>
            <ul class="navbar-nav">
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                        <span id="nav-username">Профиль</span>
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="/profile/">Профиль</a></li>
                        <li><hr class="dropdown-divider"></hr></li>
                        <li><a class="dropdown-item" href="#" onclick="logout()">Выйти</a></li>
                    </ul>
                </li>
            </ul>`;
        loadUserInfo();
    } else {
        navContent.innerHTML = `
            <ul class="navbar-nav flex-grow-1"><li class="nav-item"><a class="nav-link" href="/">Главная</a></li></ul>
            <div class="d-flex gap-2">
                <a href="/login/" class="btn btn-outline-light btn-sm">Войти</a>
                <a href="/register/" class="btn btn-light btn-sm">Регистрация</a>
            </div>`;
    }
})();

async function loadUserInfo() {
    try {
        const profile = await api.get('/users/me/');
        document.getElementById('nav-username').textContent = profile.last_name + ' ' + profile.first_name?.[0] + '.';
    } catch(e) {}
}