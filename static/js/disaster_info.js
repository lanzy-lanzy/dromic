document.addEventListener('DOMContentLoaded', function() {
    loadDisasters();

    document.getElementById('saveDisaster').addEventListener('click', function() {
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
    return `
        <div class="col-md-4 mb-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${disaster.name}</h5>
                    <p class="card-text">${disaster.description}</p>
                    <p class="card-text"><small class="text-muted">Date: ${disaster.date_occurred}</small></p>
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

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(disasterCounts),
            datasets: [{
                label: 'Number of Disasters',
                data: Object.values(disasterCounts),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
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
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addDisasterModal'));
            modal.hide();
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

    
