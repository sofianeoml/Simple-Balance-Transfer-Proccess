let offset = 5;

// Logout button
document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/logout', { method: 'GET', credentials: 'include' });
        if (response.ok) window.location.href = '/login';
    } catch (error) {
        console.error('Logout failed:', error);
    }
});

// View More button
document.getElementById('viewMoreBtn').addEventListener('click', async () => {
    try {
        const response = await fetch(`/api/users?offset=${offset}`, { method: 'GET', credentials: 'include' });
        const data = await response.json();

        const usersList = document.getElementById('usersList');
        if (data.users && data.users.length > 0) {
            data.users.forEach(user => {
                const li = document.createElement('li');
                li.className = 'user-item';
                li.innerHTML = `<span>${user.username} - Balance: $${user.balance.toFixed(2)}</span>`;
                usersList.appendChild(li);
            });
            offset += 5;
        } else {
            const li = document.createElement('li');
            li.className = 'no-users';
            li.textContent = 'No more users found';
            usersList.appendChild(li);
            document.getElementById('viewMoreBtn').disabled = true;
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
});

// Transfer button - Open dialog
const transferBtn = document.getElementById('transferBtn');
const transferDialog = document.getElementById('transferDialog');
transferBtn.addEventListener('click', () => {
    transferDialog.classList.remove('hidden');
});

// Close button - Close dialog
const closeDialogBtn = document.getElementById('closeDialogBtn');
closeDialogBtn.addEventListener('click', () => {
    transferDialog.classList.add('hidden');
    clearTransferForm();
});

// Username suggestions
document.getElementById('transferUsername').addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    const suggestionsList = document.getElementById('usernameSuggestions');
    suggestionsList.innerHTML = '';
    suggestionsList.classList.add('hidden');

    if (query.length > 0) {
        try {
            const response = await fetch(`/api/users?offset=0`, { method: 'GET', credentials: 'include' });
            const data = await response.json();
            const matches = data.users.filter(user => user.username.toLowerCase().includes(query.toLowerCase()));

            if (matches.length > 0) {
                suggestionsList.classList.remove('hidden');
                matches.forEach(user => {
                    const li = document.createElement('li');
                    li.textContent = user.username;
                    li.addEventListener('click', () => {
                        document.getElementById('transferUsername').value = user.username;
                        suggestionsList.classList.add('hidden');
                    });
                    suggestionsList.appendChild(li);
                });
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }
});

// Submit transfer - Allow negative amounts to reach the server
document.getElementById('submitTransferBtn').addEventListener('click', async () => {
    const username = document.getElementById('transferUsername').value.trim();
    const amount = parseFloat(document.getElementById('transferAmount').value);
    const messageDiv = document.getElementById('transferMessage');

    // Bug: Removed amount <= 0 check to allow negative transfers
    if (!username || isNaN(amount)) {
        showMessage(messageDiv, 'Please enter a valid username and amount', false);
        return;
    }

    try {
        const response = await fetch('/api/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, amount }),
            credentials: 'include'
        });
        const result = await response.json();

        showMessage(messageDiv, result.message, result.result);
        if (result.result) {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    } catch (error) {
        showMessage(messageDiv, 'Transfer failed. Please try again.', false);
    }
});

function showMessage(div, text, success) {
    div.classList.remove('hidden');
    div.textContent = text;
    div.classList.toggle('success', success);
    div.classList.toggle('error', !success);
}

function clearTransferForm() {
    document.getElementById('transferUsername').value = '';
    document.getElementById('transferAmount').value = '';
    const messageDiv = document.getElementById('transferMessage');
    messageDiv.classList.add('hidden');
    messageDiv.textContent = '';
    document.getElementById('usernameSuggestions').classList.add('hidden');
}