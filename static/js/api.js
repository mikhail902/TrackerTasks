const API_BASE = 'http://localhost:8000/api';

const api = {
    async request(method, url, data = null) {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };
        const token = localStorage.getItem('access');
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const config = { method, headers };
        if (data) config.body = JSON.stringify(data);

        try {
            const response = await fetch(API_BASE + url, config);

            if (response.status === 401) {
                localStorage.removeItem('access');
                localStorage.removeItem('refresh');
                window.location.href = '/login/';
                return null;
            }

            const result = await response.json();

            if (!response.ok) {
                console.error('API Error:', result);
                throw result;
            }

            return result;
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
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