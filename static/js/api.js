const api = {
    async request(method, url, data = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('access');
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const config = { method, headers };
        if (data) config.body = JSON.stringify(data);

        const response = await fetch('http://localhost:8000/api${url}', config);

        if (response.status === 401) {
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            window.location.href = '/login/';
            return;
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw error;
        }

        return response.json();
    },

    get(url) { return this.request('GET', url); },
    post(url, data) { return this.request('POST', url, data); },
    patch(url, data) { return this.request('PATCH', url, data); },
    delete(url) { return this.request('DELETE', url); }
};

function logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login/';
}