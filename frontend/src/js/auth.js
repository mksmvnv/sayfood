document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('authOverlay');
    const app = document.getElementById('app');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authButtons = document.querySelector('.auth-buttons');
    const authMessage = document.getElementById('authMessage');

    document.getElementById('showLoginBtn').addEventListener('click', () => {
        authButtons.classList.add('hidden');
        showElement(loginForm);
        hideElement(registerForm);
        authMessage.textContent = '';
    });

    document.getElementById('showRegisterBtn').addEventListener('click', () => {
        authButtons.classList.add('hidden');
        hideElement(loginForm);
        showElement(registerForm);
        authMessage.textContent = '';
    });

    document.getElementById('switchToRegister').addEventListener('click', (e) => {
        e.preventDefault();
        hideElement(loginForm);
        showElement(registerForm);
        authMessage.textContent = '';
    });

    document.getElementById('switchToLogin').addEventListener('click', (e) => {
        e.preventDefault();
        showElement(loginForm);
        hideElement(registerForm);
        authMessage.textContent = '';
    });

    document.getElementById('registerBtn').addEventListener('click', async () => {
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;

        try {
            await apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            authMessage.textContent = 'Регистрация успешна! Теперь войдите.';
            authMessage.className = 'auth-message auth-message--success';
            hideElement(registerForm);
            showElement(loginForm);
        } catch (err) {
            authMessage.textContent = err.message;
            authMessage.className = 'auth-message auth-message--error';
        }
    });

    document.getElementById('loginBtn').addEventListener('click', async () => {
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        try {
            await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            await enterApp(email);
        } catch (err) {
            authMessage.textContent = err.message;
            authMessage.className = 'auth-message auth-message--error';
        }
    });

    document.getElementById('logoutBtn').addEventListener('click', async () => {
        try {
            await apiRequest('/auth/logout', { method: 'POST' });
        } catch (err) {
            console.error('Logout error:', err);
        } finally {
            deleteCookie('sf_session_id');
            localStorage.removeItem('userEmail');
            hideElement(app);
            showElement(overlay);
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPassword').value = '';
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerPassword').value = '';
            authMessage.textContent = '';
            authButtons.classList.remove('hidden');
            hideElement(loginForm);
            hideElement(registerForm);
            document.getElementById('resultContainer').classList.remove('show');
            document.getElementById('resultContainer').innerHTML = '';
        }
    });

    checkSession();
});

async function enterApp(email) {
    hideElement(document.getElementById('authOverlay'));
    showElement(document.getElementById('app'));
    document.getElementById('userEmailDisplay').textContent = email;
    localStorage.setItem('userEmail', email);
    await updateRemainingRequests();
    await loadHistory();
}

async function checkSession() {
    try {
        const user = await apiRequest('/auth/me', { method: 'GET' });
        await enterApp(user.email);
    } catch {
        hideElement(document.getElementById('app'));
        showElement(document.getElementById('authOverlay'));
    }
}
