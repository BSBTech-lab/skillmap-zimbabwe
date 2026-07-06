// SkillMap Zimbabwe - Dashboard Initialization & Dynamic Data Filtering
document.addEventListener('DOMContentLoaded', function () {
    
    // 1. Core Platform Configuration & Brand Colors
    const BRAND_TEAL = '#16666A';
    const BRAND_GOLD = '#CAA84F';
    const DARK_TEAL  = '#123F42';

    // 2. Localized Data Store
    const originalDataset = {
        'All Regions': {
            labels: ['Agriculture', 'Mining', 'Technology', 'Health', 'Energy', 'Finance', 'Tourism'],
            demand: [80, 75, 90, 65, 85, 70, 55],
            supply: [60, 50, 45, 60, 40, 65, 65]
        },
        'Harare': {
            labels: ['Technology', 'Finance', 'Health', 'Agriculture'],
            demand: [95, 85, 70, 40],
            supply: [75, 70, 55, 30]
        },
        'Bulawayo': {
            labels: ['Manufacturing', 'Finance', 'Technology', 'Tourism'],
            demand: [85, 75, 70, 80],
            supply: [50, 60, 50, 65]
        },
        'Matabeleland': {
            labels: ['Energy', 'Mining', 'Agriculture', 'Tourism'],
            demand: [95, 90, 75, 70],
            supply: [25, 45, 55, 50]
        }
    };

    // 3. Initialize Blank Chart Context
    const ctx = document.getElementById('supplyDemandChart').getContext('2d');
    let supplyDemandChart;

    // Fixed parameters to accept arrays cleanly
    function renderChart(labels, demandData, supplyData) {
        if (supplyDemandChart) {
            supplyDemandChart.destroy();
        }

        supplyDemandChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Industry Demand (%)',
                        data: demandData,
                        backgroundColor: BRAND_TEAL,
                        borderRadius: 6
                    },
                    {
                        label: 'Skills Supply (%)',
                        data: supplyData, // FIXED: Now uses the scoped parameter parameter instead of activeData
                        backgroundColor: BRAND_GOLD,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: DARK_TEAL, font: { weight: '600', family: 'Segoe UI' } }
                    }
                },
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: '#E0E4E4' }, ticks: { color: DARK_TEAL } },
                    x: { grid: { display: false }, ticks: { color: DARK_TEAL } }
                }
            }
        });
    }

    // 4. Filter Interaction Brains
    function applyDashboardFilters() {
        const selectElements = document.querySelectorAll('.filter-select');
        
        const selectedRegion = selectElements[0].value;
        const selectedSector = selectElements[1].value;

        let activeData = originalDataset[selectedRegion] || originalDataset['All Regions'];

        if (selectedSector !== 'All Sectors') {
            const index = activeData.labels.indexOf(selectedSector);
            if (index !== -1) {
                renderChart(
                    [activeData.labels[index]], 
                    [activeData.demand[index]], 
                    [activeData.supply[index]]
                );
                return;
            }
        }

        renderChart(activeData.labels, activeData.demand, activeData.supply);
    }

    // 5. Connect Event Listeners
    const applyButton = document.querySelector('.btn-apply');
    if (applyButton) {
        applyButton.addEventListener('click', function(e) {
            e.preventDefault();
            applyDashboardFilters();
        });
    }

    // Initial Load - Passes data parameters directly to the layout drawer
    renderChart(
        originalDataset['All Regions'].labels,
        originalDataset['All Regions'].demand,
        originalDataset['All Regions'].supply
    );
});
