document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('profileModal');
    const showProfileBtn = document.getElementById('showProfileBtn');
    const closeModal = document.querySelector('.close-modal');
    const profileMessage = document.getElementById('profileMessage');

    showProfileBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
        profileMessage.textContent = '';
        profileMessage.className = 'profile-message';
    });

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const oldPassword = document.getElementById('oldPassword').value;
        const newPassword = document.getElementById('newPassword').value;

        try {
            await apiRequest('/auth/me/password', {
                method: 'POST',
                body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
            });
            profileMessage.textContent = 'Пароль изменён. Войдите снова.';
            profileMessage.className = 'profile-message profile-message--success';
            document.getElementById('oldPassword').value = '';
            document.getElementById('newPassword').value = '';
            showToast('Пароль обновлён', 'success');
        } catch (err) {
            profileMessage.textContent = err.message;
            profileMessage.className = 'profile-message profile-message--error';
        }
    });

    document.getElementById('changeEmailForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const oldEmail = document.getElementById('oldEmail').value.trim();
        const newEmail = document.getElementById('newEmail').value.trim();

        try {
            await apiRequest('/auth/me/email', {
                method: 'POST',
                body: JSON.stringify({ old_email: oldEmail, new_email: newEmail }),
            });
            profileMessage.textContent = 'Email изменён. Войдите снова.';
            profileMessage.className = 'profile-message profile-message--success';
            document.getElementById('oldEmail').value = '';
            document.getElementById('newEmail').value = '';
            document.getElementById('userEmailDisplay').textContent = newEmail;
            localStorage.setItem('userEmail', newEmail);
            showToast('Email обновлён', 'success');
        } catch (err) {
            profileMessage.textContent = err.message;
            profileMessage.className = 'profile-message profile-message--error';
        }
    });
});
