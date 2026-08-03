document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('mealPlanForm');
    const resultContainer = document.getElementById('resultContainer');
    const generateBtn = document.getElementById('generateBtn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const allergies = Array.from(
            document.querySelectorAll('#allergiesGroup input[type="checkbox"]:checked')
        ).map((cb) => cb.value);

        const restrictions = Array.from(
            document.querySelectorAll('#restrictionsGroup input[type="checkbox"]:checked')
        ).map((cb) => cb.value);

        const data = {
            goal: document.getElementById('goal').value,
            weight: parseFloat(document.getElementById('weight').value),
            height: parseFloat(document.getElementById('height').value),
            age: parseInt(document.getElementById('age').value, 10),
            gender: document.getElementById('gender').value,
            activity_level: document.getElementById('activityLevel').value,
            allergies,
            restrictions,
        };

        generateBtn.disabled = true;
        generateBtn.classList.add('btn--loading');
        resultContainer.classList.remove('show');

        try {
            const response = await apiRequest('/meal_plan/generate', {
                method: 'POST',
                body: JSON.stringify(data),
            });

            resultContainer.innerHTML = `
                <div class="result-header">
                    <span class="result-badge">Готово</span>
                    <time>${formatDate(response.created_at)}</time>
                </div>
                <div class="result-body">${formatPlanText(response.plan)}</div>
            `;
            resultContainer.classList.add('show');
            showToast('План питания сгенерирован', 'success');
            await updateRemainingRequests();
            await loadHistory();
        } catch (err) {
            resultContainer.innerHTML = `<div class="result-error">${err.message}</div>`;
            resultContainer.classList.add('show');
            showToast(err.message, 'error');
        } finally {
            generateBtn.disabled = false;
            generateBtn.classList.remove('btn--loading');
        }
    });
});

async function updateRemainingRequests() {
    const badge = document.getElementById('requestsRemaining');
    try {
        const data = await apiRequest('/meal_plan/remaining');
        badge.textContent = `${data.remaining} / ${data.daily_limit}`;
        badge.dataset.low = data.remaining <= 1 ? 'true' : 'false';
    } catch {
        badge.textContent = '—';
    }
}

async function loadHistory() {
    const container = document.getElementById('historyList');
    try {
        const data = await apiRequest('/meal_plan/history?limit=10');
        if (!data || data.length === 0) {
            container.innerHTML = '<p class="empty-state">Пока нет сохранённых планов</p>';
            return;
        }

        container.innerHTML = data
            .map(
                (item) => `
            <article class="history-card" data-id="${item.id}">
                <div class="history-card__meta">
                    <span class="history-card__goal">${goalLabel(item.goal)}</span>
                    <time>${formatDate(item.created_at)}</time>
                </div>
                <p class="history-card__params">${item.weight} кг · ${item.height} см</p>
                <p class="history-card__preview">${item.plan.slice(0, 120)}…</p>
            </article>
        `
            )
            .join('');

        container.querySelectorAll('.history-card').forEach((card) => {
            card.addEventListener('click', () => {
                const item = data.find((entry) => entry.id === card.dataset.id);
                if (!item) return;

                const resultContainer = document.getElementById('resultContainer');
                resultContainer.innerHTML = `
                    <div class="result-header">
                        <span class="result-badge">${goalLabel(item.goal)}</span>
                        <time>${formatDate(item.created_at)}</time>
                    </div>
                    <div class="result-body">${formatPlanText(item.plan)}</div>
                `;
                resultContainer.classList.add('show');
                resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });
        });
    } catch {
        container.innerHTML = '<p class="empty-state empty-state--error">Не удалось загрузить историю</p>';
    }
}
