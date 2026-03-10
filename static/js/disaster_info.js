document.addEventListener('DOMContentLoaded', function () {
    loadDisasters();

    document.getElementById('saveDisaster').addEventListener('click', function () {
        saveDisaster();
    });

    const updateBtn = document.getElementById('updateDisaster');
    if (updateBtn) {
        updateBtn.addEventListener('click', function () {
            updateDisaster();
        });
    }
});

// Store disaster data globally for Alpine.js access
window._disasterData = [];

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : '';
}

function loadDisasters() {
    fetch('/api/disasters/')
        .then(response => response.json())
        .then(data => {
            window._disasterData = data;
            // Push data into Alpine via custom event
            window.dispatchEvent(new CustomEvent('disasters-loaded', { detail: data }));
            updateDashboard(data);
            createDisasterChart(data);
        })
        .catch(error => console.error('Error loading disasters:', error));
}

function updateDashboard(disasters) {
    const recentEl = document.getElementById('recentDisaster');
    if (recentEl && disasters.length > 0) {
        const mostRecent = disasters.reduce((a, b) =>
            new Date(a.date_occurred) > new Date(b.date_occurred) ? a : b
        );
        recentEl.textContent = mostRecent.name;
    } else if (recentEl) {
        recentEl.textContent = 'None';
    }
}

function createDisasterChart(disasters) {
    const canvas = document.getElementById('disasterChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const disasterCounts = {};

    disasters.forEach(disaster => {
        const year = new Date(disaster.date_occurred).getFullYear();
        disasterCounts[year] = (disasterCounts[year] || 0) + 1;
    });

    if (window.disasterChartInstance) {
        window.disasterChartInstance.destroy();
    }

    window.disasterChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(disasterCounts),
            datasets: [{
                label: 'Number of Disasters',
                data: Object.values(disasterCounts),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function saveDisaster() {
    const form = document.getElementById('addDisasterForm');
    const formData = new FormData(form);

    fetch('/api/disasters/create/', {
        method: 'POST',
        headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.dispatchEvent(new CustomEvent('close-modals'));
                form.reset();
                loadDisasters();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while saving the disaster.');
        });
}

function updateDisaster() {
    const form = document.getElementById('editDisasterForm');
    const formData = new FormData(form);
    const id = document.getElementById('editDisasterId').value;

    fetch(`/api/disasters/${id}/update/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.dispatchEvent(new CustomEvent('close-modals'));
                form.reset();
                loadDisasters();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the disaster.');
        });
}

window.editDisaster = function(id) {
    const disaster = window._disasterData.find(d => d.id === id);
    if (disaster) {
        document.getElementById('editDisasterId').value = disaster.id;
        document.getElementById('editDisasterName').value = disaster.name;
        document.getElementById('editDisasterDescription').value = disaster.description;
        document.getElementById('editDisasterDate').value = disaster.date_occurred;
        window.dispatchEvent(new CustomEvent('open-edit-modal'));
    }
};

window.deleteDisaster = function(id) {
    if (!confirm('Are you sure you want to delete this disaster?')) return;

    fetch('/api/disasters/' + id + '/delete/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadDisasters();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the disaster.');
        });
};

// Expose bulk delete globally for Alpine.js button
window.bulkDeleteDisasters = function (ids) {
    fetch('/api/disasters/bulk-delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ ids: ids })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadDisasters();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting disasters.');
        });
};
