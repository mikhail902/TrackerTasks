async function loadTasks() {
    const tasks = await api.get('/tasks/');
    const statuses = ['backlog', 'todo', 'in_progress', 'done'];

    statuses.forEach(status => {
        const container = document.getElementById(status);
        const filtered = tasks.results.filter(t => t.status === status);
        container.innerHTML = filtered.map(t => `
            <div class="card mb-2 ${t.priority === 'high' ? 'border-danger' : ''}">
                <div class="card-body p-2">
                    <a href="/tasks/${t.id}/" class="text-decoration-none">${t.title}</a>
                    <small class="text-muted d-block">${t.assignee?.full_name || '—'}</small>
                </div>
            </div>
        `).join('');
    });
}

async function createTask() {
    const form = document.getElementById('taskForm');
    const data = Object.fromEntries(new FormData(form));
    await api.post('/tasks/', data);
    location.reload();
}

loadTasks();