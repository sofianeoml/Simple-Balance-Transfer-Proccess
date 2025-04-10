document.getElementById('processBtn').addEventListener('click', async () => {
    const processBtn = document.getElementById('processBtn');
    const resultsDiv = document.getElementById('results');
    const resultsBody = document.getElementById('resultsBody');
    
    processBtn.disabled = true;
    processBtn.textContent = 'Processing...';
    resultsBody.innerHTML = '';
    resultsDiv.classList.add('hidden');

    try {
        const response = await fetch('/api/check_transactions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        const data = await response.json();

        resultsDiv.classList.remove('hidden');
        data.results.forEach(result => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${result.transaction_id || 'N/A'}</td>
                <td>${result.errors.length > 0 ? result.errors.join(', ') : 'None'}</td>
                <td class="${result.status.includes('Error') ? 'error' : 'success'}">${result.status}</td>
            `;
            resultsBody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error processing transactions:', error);
        resultsDiv.classList.remove('hidden');
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="3" class="error">Error: ${error.message}</td>`;
        resultsBody.appendChild(tr);
    } finally {
        processBtn.disabled = false;
        processBtn.textContent = 'Process Transactions';
    }
});