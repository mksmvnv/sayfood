const rawBase = window.APP_CONFIG?.apiBase ?? 'http://localhost:8000';
const API_BASE = rawBase.includes('__API_BASE__') ? 'http://localhost:8000' : rawBase;

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
        credentials: 'include',
    });

    const text = await response.text();
    let data;
    try {
        data = JSON.parse(text);
    } catch {
        data = { detail: text || 'Unknown error' };
    }

    if (!response.ok) {
        throw new Error(data.detail || data.code || `HTTP ${response.status}`);
    }

    return data;
}
