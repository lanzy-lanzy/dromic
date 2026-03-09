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

// Helper: get the Alpine.js component data from the disaster info container
function getAlpineData() {
    if (!window.Alpine) return null;
    const containers = document.querySelectorAll('[x-data]');
    for (const el of containers) {
        const data = Alpine.$data(el);
        if (data && 'selectedIds' in data) return data;
    }
    return null;
}

function loadDisasters() {
    fetch('/api/disasters/')
        .then(response => response.json())
        .then(data => {
            window._disasterData = data;
            updateDashboard(data);
            renderDisasterList(data);
            renderDisasterTable(data);
            createDisasterChart(data);
        })
        .catch(error => console.error('Error loading disasters:', error));
}

function updateDashboard(disasters) {
    const totalEl = document.getElementById('totalDisasters');
    const recentEl = document.getElementById('recentDisaster');

    if (totalEl) totalEl.textContent = disasters.length;
    if (recentEl && disasters.length > 0) {
        const mostRecent = disasters.reduce((a, b) =>
            new Date(a.date_occurred) > new Date(b.date_occurred) ? a : b
        );
        recentEl.textContent = mostRecent.name;
    } else if (recentEl) {
        recentEl.textContent = 'None';
    }
}

function renderDisasterList(disasters) {
    const disasterList = document.getElementById('disasterList');
    if (!disasterList) return;
    disasterList.innerHTML = '';
    disasters.forEach(disaster => {
        const card = document.createElement('div');
        card.innerHTML = createDisasterCard(disaster);
        const cardEl = card.firstElementChild;

        // Bind checkbox
        const cb = cardEl.querySelector('.disaster-checkbox');
        if (cb) {
            cb.checked = isSelected(disaster.id);
            cb.addEventListener('change', function () {
                toggleSelection(disaster.id);
                syncAllCheckboxes();
            });
        }

        // Bind edit button
        const editBtn = cardEl.querySelector('.edit-btn');
        if (editBtn) editBtn.addEventListener('click', () => editDisaster(disaster.id));

        // Bind delete button
        const deleteBtn = cardEl.querySelector('.delete-btn');
        if (deleteBtn) deleteBtn.addEventListener('click', () => deleteDisaster(disaster.id));

        disasterList.appendChild(cardEl);
    });
}

function renderDisasterTable(disasters) {
    const tableBody = document.getElementById('disasterTableBody');
    if (!tableBody) return;
    tableBody.innerHTML = '';
    disasters.forEach(disaster => {
        const wrapper = document.createElement('tbody');
        wrapper.innerHTML = createDisasterRow(disaster);
        const row = wrapper.firstElementChild;

        // Bind checkbox
        const cb = row.querySelector('.disaster-checkbox');
        if (cb) {
            cb.checked = isSelected(disaster.id);
            cb.addEventListener('change', function () {
                toggleSelection(disaster.id);
                syncAllCheckboxes();
            });
        }

        // Bind edit button
        const editBtn = row.querySelector('.edit-btn');
        if (editBtn) editBtn.addEventListener('click', () => editDisaster(disaster.id));

        // Bind delete button
        const deleteBtn = row.querySelector('.delete-btn');
        if (deleteBtn) deleteBtn.addEventListener('click', () => deleteDisaster(disaster.id));

        tableBody.appendChild(row);
    });
}

// Selection state helpers — use Alpine data if available
function isSelected(id) {
    const data = getAlpineData();
    if (data) return data.selectedIds.indexOf(id) > -1;
    return false;
}

function toggleSelection(id) {
    const data = getAlpineData();
    if (!data) return;
    const idx = data.selectedIds.indexOf(id);
    if (idx > -1) data.selectedIds.splice(idx, 1);
    else data.selectedIds.push(id);
}

function clearSelection() {
    const data = getAlpineData();
    if (data) {
        data.selectedIds = [];
        data.allSelected = false;
    }
}

function syncAllCheckboxes() {
    // Sync all card and table checkboxes with Alpine state
    document.querySelectorAll('.disaster-checkbox').forEach(cb => {
        const id = parseInt(cb.dataset.id);
        if (!isNaN(id)) cb.checked = isSelected(id);
    });
}

function createDisasterCard(disaster) {
    const formattedDate = new Date(disaster.date_occurred).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
    });

    return `
        <div class="bg-white rounded-2xl shadow-md border border-slate-100 hover:shadow-lg transition-all duration-300 overflow-hidden group">
            <div class="px-5 py-4 border-b border-slate-100 bg-white">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <input type="checkbox" class="w-4 h-4 rounded border-slate-300 text-red-500 focus:ring-red-400 mr-3 cursor-pointer disaster-checkbox" data-id="${disaster.id}">
                        <h5 class="text-lg font-bold text-slate-800 flex items-center capitalize">
                            <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                            ${disaster.name}
                        </h5>
                    </div>
                </div>
            </div>
            <div class="p-5">
                <p class="text-slate-600 mb-4 line-clamp-2">${disaster.description}</p>
                <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div class="flex items-center text-sm text-gray-500">
                        <i class="fas fa-calendar-alt mr-2"></i>
                        ${formattedDate}
                    </div>
                    <div class="flex space-x-2">
                        <button class="edit-btn w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-500 hover:bg-blue-200 transition-colors">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="delete-btn w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-500 hover:bg-red-200 transition-colors">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createDisasterRow(disaster) {
    const formattedDate = new Date(disaster.date_occurred).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
    });

    return `
        <tr class="hover:bg-slate-50 transition-colors">
            <td class="px-5 py-4">
                <input type="checkbox" class="w-4 h-4 rounded border-slate-300 text-red-500 focus:ring-red-400 cursor-pointer disaster-checkbox" data-id="${disaster.id}">
            </td>
            <td class="px-5 py-4">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-triangle text-red-500 mr-3 text-sm"></i>
                    <span class="font-semibold text-slate-800 capitalize">${disaster.name}</span>
                </div>
            </td>
            <td class="px-5 py-4 text-slate-600 max-w-xs truncate">${disaster.description}</td>
            <td class="px-5 py-4 text-slate-500 text-sm">
                <i class="fas fa-calendar-alt mr-2 text-slate-400"></i>
                ${formattedDate}
            </td>
            <td class="px-5 py-4 text-right">
                <div class="flex justify-end space-x-2">
                    <button class="edit-btn w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-500 hover:bg-blue-200 transition-colors">
                        <i class="fas fa-edit text-sm"></i>
                    </button>
                    <button class="delete-btn w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-500 hover:bg-red-200 transition-colors">
                        <i class="fas fa-trash text-sm"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
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

function editDisaster(id) {
    fetch('/api/disasters/')
        .then(response => response.json())
        .then(disasters => {
            const disaster = disasters.find(d => d.id === id);
            if (disaster) {
                document.getElementById('editDisasterId').value = disaster.id;
                document.getElementById('editDisasterName').value = disaster.name;
                document.getElementById('editDisasterDescription').value = disaster.description;
                document.getElementById('editDisasterDate').value = disaster.date_occurred;
                window.dispatchEvent(new CustomEvent('open-edit-modal'));
            }
        })
        .catch(error => console.error('Error:', error));
}

function deleteDisaster(id) {
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
}

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
                clearSelection();
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

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : '';
}
