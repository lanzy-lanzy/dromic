document.addEventListener('DOMContentLoaded', function () {
    loadDisasters();

    document.getElementById('saveDisaster').addEventListener('click', function () {
        saveDisaster();
    });
});

function loadDisasters() {
    fetch('/api/disasters/')
        .then(response => response.json())
        .then(data => {
            updateDashboard(data);
            renderDisasterList(data);
            createDisasterChart(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateDashboard(disasters) {
    document.getElementById('totalDisasters').textContent = disasters.length;
    if (disasters.length > 0) {
        const mostRecent = disasters.reduce((a, b) => new Date(a.date_occurred) > new Date(b.date_occurred) ? a : b);
        document.getElementById('recentDisaster').textContent = mostRecent.name;
    }
}

function renderDisasterList(disasters) {
    const disasterList = document.getElementById('disasterList');
    disasterList.innerHTML = '';
    disasters.forEach(disaster => {
        disasterList.innerHTML += createDisasterCard(disaster);
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
                    <h5 class="text-lg font-bold text-slate-800 flex items-center capitalize">
                        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                        ${disaster.name}
                    </h5>
                    <button class="text-slate-400 hover:text-slate-600 transition-colors">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
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
                        <button class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-500 hover:bg-blue-200 transition-colors" onclick="editDisaster(${disaster.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center text-red-500 hover:bg-red-200 transition-colors" onclick="deleteDisaster(${disaster.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createDisasterChart(disasters) {
    const ctx = document.getElementById('disasterChart').getContext('2d');
    const disasterCounts = {};

    disasters.forEach(disaster => {
        const year = new Date(disaster.date_occurred).getFullYear();
        disasterCounts[year] = (disasterCounts[year] || 0) + 1;
    });

    // Destroy existing chart if it exists to prevent overlapping
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
                borderColor: '#10b981', // emerald-500
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
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function saveDisaster() {
    const form = document.getElementById('addDisasterForm');
    const formData = new FormData(form);

    fetch('/api/disasters/create/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.dispatchEvent(new CustomEvent('close-modals'));
                loadDisasters();
                form.reset();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while saving the disaster.');
        });
}

function editDisaster(id) {
    console.log('Edit disaster feature coming soon for id: ', id);
    // TODO: fetch disaster details and populate edit modal
}

function deleteDisaster(id) {
    if (confirm('Are you sure you want to delete this disaster?')) {
        console.log('Delete disaster feature coming soon for id: ', id);
        // TODO: implement delete request
    }
}


