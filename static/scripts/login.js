document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password'),
    };

    const messageDiv = document.getElementById('message');

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const result = await response.json();

        messageDiv.classList.remove('hidden');
        messageDiv.textContent = result.message || (result.result ? 'Login successful!' : 'Something went wrong!');
        messageDiv.classList.toggle('success', result.result);
        messageDiv.classList.toggle('error', !result.result);

        if (result.result) {
            setTimeout(() => {
                window.location.href = '/profile';  // Explicit redirect to profile
            }, 3000);
        }
    } catch (error) {
        messageDiv.classList.remove('hidden');
        messageDiv.classList.add('error');
        messageDiv.classList.remove('success');
        messageDiv.textContent = 'An error occurred. Please try again.';
    }
});