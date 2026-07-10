// SkillMap Zimbabwe - Dashboard with Real Data Integration
// Version: 2.0 - Connected to skills_matrix.json

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 SkillMap Zimbabwe Dashboard loading...');

    // ============================================
    // 1. BRAND COLORS (Fixed - Do Not Change)
    // ============================================
    const BRAND_TEAL = '#16666A';
    const BRAND_GOLD = '#CAA84F';
    const DARK_TEAL = '#123F42';
    const LIGHT_CREAM = '#F7F6F2';

    // ============================================
    // 2. GLOBAL STATE
    // ============================================
    let fullDataset = null; // Will hold the loaded JSON
    let supplyDemandChart = null; // Chart.js instance
    let currentFilteredData = null; // Currently displayed data

    // ============================================
    // 3. LOAD JSON DATA FROM FILE
    // ============================================
    async function loadData() {
        try {
            console.log('📊 Loading skills data...');
            
            // Try loading from data folder
            const response = await fetch('./data/skills_matrix.json');
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            fullDataset = data;
            console.log('✅ Data loaded successfully!');
            console.log(`📊 Found ${fullDataset.skills_matrix.length} sectors`);
            
            // Process data and initialize dashboard
            processDataAndRender();
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            console.warn('⚠️ Falling back to dummy data...');
            
            // Fallback to dummy data if JSON fails to load
            fullDataset = getDummyData();
            processDataAndRender();
        }
    }

    // ============================================
    // 4. DUMMY DATA FALLBACK (For testing)
    // ============================================
    function getDummyData() {
        return {
            skills_matrix: [
                {
                    sector_name: "ICT",
                    regional_breakdown: [
                        {
                            province: "Harare",
                            deficit_skills: [
                                { skill: "Cybersecurity", mismatch_index: 95 },
                                { skill: "Network Engineering", mismatch_index: 92 },
                                { skill: "Data Analytics", mismatch_index: 86 }
                            ],
                            surplus_skills: [
                                "General Computer Science Graduates",
                                "General IT Graduates"
                            ],
                            visibility_score: 0.7
                        },
                        {
                            province: "Bulawayo",
                            deficit_skills: [
                                { skill: "ICT Product Sales", mismatch_index: 65 }
                            ],
                            surplus_skills: [],
                            visibility_score: 0.7
                        }
                    ]
                },
                {
                    sector_name: "Agriculture",
                    regional_breakdown: [
                        {
                            province: "Harare",
                            deficit_skills: [
                                { skill: "Farm Supervisor", mismatch_index: 50 }
                            ],
                            surplus_skills: [],
                            visibility_score: 0.7
                        }
                    ]
                }
            ]
        };
    }

    // ============================================
    // 5. PROCESS DATA & RENDER DASHBOARD
    // ============================================
    function processDataAndRender() {
        if (!fullDataset || !fullDataset.skills_matrix) {
            console.error('❌ No data to render!');
            return;
        }

        // Build the dataset for the chart
        const chartData = buildChartData(fullDataset);
        
        // Render the chart
        renderChart(chartData.labels, chartData.demand, chartData.supply);
        
        // Update KPI cards
        updateKPIs(fullDataset);
        
        // Build insight cards
        buildInsightCards(fullDataset);
        
        // Build recommended actions
        buildRecommendedActions(fullDataset);
        
        // Populate filter dropdowns
        populateFilters(fullDataset);
        
        console.log('✅ Dashboard fully rendered!');
    }

    // ============================================
    // 6. BUILD CHART DATA FROM JSON
    // ============================================
    function buildChartData(data) {
        const labels = [];
        const demand = [];
        const supply = [];

        data.skills_matrix.forEach(sector => {
            // Use sector name as label
            labels.push(sector.sector_name);
            
            // Calculate average demand from deficit skills (higher mismatch = higher demand)
            let totalDemand = 0;
            let totalSupply = 0;
            let deficitCount = 0;
            let surplusCount = 0;

            // Process each region in this sector
            sector.regional_breakdown.forEach(region => {
                // Deficit skills = high demand (mismatch index = demand)
                region.deficit_skills.forEach(skill => {
                    totalDemand += skill.mismatch_index;
                    deficitCount++;
                });
                
                // Surplus skills = supply (we use a base value since it's text)
                region.surplus_skills.forEach(() => {
                    totalSupply += 40; // Base supply value for surplus skills
                    surplusCount++;
                });
            });

            // Calculate averages
            const avgDemand = deficitCount > 0 ? Math.round(totalDemand / deficitCount) : 30;
            const avgSupply = surplusCount > 0 ? Math.round(totalSupply / surplusCount) : 30;

            // Cap at 100
            demand.push(Math.min(avgDemand, 100));
            supply.push(Math.min(avgSupply, 100));
        });

        return { labels, demand, supply };
    }

    // ============================================
    // 7. RENDER CHART
    // ============================================
    function renderChart(labels, demandData, supplyData) {
        const canvas = document.getElementById('supplyDemandChart');
        if (!canvas) {
            console.error('❌ Canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');

        // Destroy existing chart
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
                        borderRadius: 6,
                        maxBarThickness: 40,
                        hoverBackgroundColor: '#1a7a7e'
                    },
                    {
                        label: 'Skills Supply (%)',
                        data: supplyData,
                        backgroundColor: BRAND_GOLD,
                        borderRadius: 6,
                        maxBarThickness: 40,
                        hoverBackgroundColor: '#dbb85e'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: DARK_TEAL,
                            font: { weight: '600', size: 12 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: DARK_TEAL,
                        titleColor: '#FFFFFF',
                        bodyColor: LIGHT_CREAM,
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.06)' },
                        ticks: { color: DARK_TEAL, font: { size: 11 } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: DARK_TEAL, font: { size: 11, weight: '500' } }
                    }
                }
            }
        });

        console.log('✅ Chart rendered with', labels.length, 'sectors');
    }

    // ============================================
    // 8. UPDATE KPI CARDS
    // ============================================
    function updateKPIs(data) {
        let totalSkills = 0;
        let sectors = data.skills_matrix.length;
        let totalGap = 0;
        let gapCount = 0;

        data.skills_matrix.forEach(sector => {
            sector.regional_breakdown.forEach(region => {
                region.deficit_skills.forEach(skill => {
                    totalSkills++;
                    totalGap += skill.mismatch_index;
                    gapCount++;
                });
            });
        });

        const avgGap = gapCount > 0 ? Math.round(totalGap / gapCount) : 0;
        
        // Training ready = skills with gap < 50 (closer to balance)
        let trainingReady = 0;
        data.skills_matrix.forEach(sector => {
            sector.regional_breakdown.forEach(region => {
                region.deficit_skills.forEach(skill => {
                    if (skill.mismatch_index < 50) trainingReady++;
                });
            });
        });

        // Update DOM
        const kpiNumbers = document.querySelectorAll('.kpi-number');
        if (kpiNumbers.length >= 4) {
            kpiNumbers[0].textContent = totalSkills || 124;
            kpiNumbers[1].textContent = sectors || 45;
            kpiNumbers[2].textContent = avgGap + '%' || '32%';
            kpiNumbers[3].textContent = trainingReady || 89;
        }

        console.log('📊 KPIs updated:', { totalSkills, sectors, avgGap, trainingReady });
    }

    // ============================================
    // 9. BUILD INSIGHT CARDS
    // ============================================
    function buildInsightCards(data) {
        const insightContainer = document.querySelector('.insights-row');
        if (!insightContainer) {
            console.warn('⚠️ Insight container not found');
            return;
        }

        // Find top deficit skills across all sectors
        let allDeficits = [];
        data.skills_matrix.forEach(sector => {
            sector.regional_breakdown.forEach(region => {
                region.deficit_skills.forEach(skill => {
                    allDeficits.push({
                        skill: skill.skill,
                        sector: sector.sector_name,
                        region: region.province,
                        mismatch: skill.mismatch_index
                    });
                });
            });
        });

        // Sort by highest mismatch (biggest gap)
        allDeficits.sort((a, b) => b.mismatch - a.mismatch);

        // Get top 2 insights
        const topInsight = allDeficits[0];
        const secondInsight = allDeficits[1] || allDeficits[0];

        // Build insight cards HTML
        insightContainer.innerHTML = `
            <div class="insight-card">
                <div class="insight-text">
                    💡 <strong>${topInsight.sector}</strong> in <strong>${topInsight.region}</strong> has a critical shortage of <strong>${topInsight.skill}</strong> (${topInsight.mismatch}% mismatch index).
                </div>
                <span class="insight-source">📌 Priority: Highest skills gap detected</span>
            </div>
            <div class="insight-card gold">
                <div class="insight-text">
                    ⚠️ <strong>${secondInsight.sector}</strong> in <strong>${secondInsight.region}</strong> needs <strong>${secondInsight.skill}</strong> with ${secondInsight.mismatch}% gap.
                </div>
                <span class="insight-source">📌 Urgent intervention recommended</span>
            </div>
        `;

        console.log('💡 Insight cards built with top deficits');
    }

    // ============================================
    // 10. BUILD RECOMMENDED ACTIONS
    // ============================================
    function buildRecommendedActions(data) {
        const actionsContainer = document.querySelector('.actions-card');
        if (!actionsContainer) {
            console.warn('⚠️ Actions container not found');
            return;
        }

        // Find top 3 sectors with highest deficit skills
        let sectorDeficitCount = [];
        data.skills_matrix.forEach(sector => {
            let deficitCount = 0;
            sector.regional_breakdown.forEach(region => {
                deficitCount += region.deficit_skills.length;
            });
            sectorDeficitCount.push({
                sector: sector.sector_name,
                deficitCount: deficitCount,
                totalMismatch: sector.regional_breakdown.reduce((sum, r) => {
                    return sum + r.deficit_skills.reduce((s, sk) => s + sk.mismatch_index, 0);
                }, 0)
            });
        });

        sectorDeficitCount.sort((a, b) => b.deficitCount - a.deficitCount || b.totalMismatch - a.totalMismatch);

        const topSectors = sectorDeficitCount.slice(0, 3);

        // Build action items
        const actionItems = topSectors.map((sector, index) => {
            const actions = {
                0: `Increase training capacity in ${sector.sector} by 20%`,
                1: `Upskill ${sector.sector} professionals in emerging areas`,
                2: `Launch ${sector.sector} development program`
            };
            
            return `
                <div class="action-item">
                    <div class="action-left">
                        <span class="action-number">${index + 1}</span>
                        <span class="action-text">${actions[index] || 'Address skills gap in ' + sector.sector}</span>
                    </div>
                    <button class="action-btn" data-action="${index + 1}">View Plan</button>
                </div>
            `;
        }).join('');

        // Update the actions section
        actionsContainer.innerHTML = `
            <div class="actions-title">⚡ Recommended Actions</div>
            ${actionItems}
        `;

        // Re-attach event listeners to action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const actionNumber = this.dataset.action;
                const actionText = this.closest('.action-item').querySelector('.action-text').textContent;
                alert(`📋 Action Plan ${actionNumber}:\n\n${actionText}\n\nDetailed plan coming soon!`);
            });
        });

        console.log('⚡ Recommended actions built');
    }

    // ============================================
    // 11. POPULATE FILTER DROPDOWNS
    // ============================================
    function populateFilters(data) {
        // Get unique sectors
        const sectors = [...new Set(data.skills_matrix.map(s => s.sector_name))];
        
        // Get unique regions
        const regions = [];
        data.skills_matrix.forEach(sector => {
            sector.regional_breakdown.forEach(region => {
                if (!regions.includes(region.province)) {
                    regions.push(region.province);
                }
            });
        });

        // Update sector dropdown
        const sectorSelect = document.querySelectorAll('.filter-select')[1];
        if (sectorSelect) {
            const currentValue = sectorSelect.value;
            sectorSelect.innerHTML = `<option value="All Sectors">All Sectors</option>`;
            sectors.sort().forEach(sector => {
                sectorSelect.innerHTML += `<option value="${sector}">${sector}</option>`;
            });
            sectorSelect.value = currentValue;
        }

        // Update region dropdown
        const regionSelect = document.querySelectorAll('.filter-select')[0];
        if (regionSelect) {
            const currentValue = regionSelect.value;
            regionSelect.innerHTML = `<option value="All Regions">All Regions</option>`;
            regions.sort().forEach(region => {
                regionSelect.innerHTML += `<option value="${region}">${region}</option>`;
            });
            regionSelect.value = currentValue;
        }

        console.log('🔍 Filters populated:', { sectors: sectors.length, regions: regions.length });
    }

    // ============================================
    // 12. FILTER LOGIC
    // ============================================
    function applyFilters() {
        const regionSelect = document.querySelectorAll('.filter-select')[0];
        const sectorSelect = document.querySelectorAll('.filter-select')[1];
        
        if (!regionSelect || !sectorSelect || !fullDataset) return;

        const selectedRegion = regionSelect.value;
        const selectedSector = sectorSelect.value;

        console.log(`🔍 Applying filters: Region=${selectedRegion}, Sector=${selectedSector}`);

        // Filter the data
        let filtered = fullDataset;

        // Filter by sector
        if (selectedSector !== 'All Sectors') {
            filtered = {
                skills_matrix: filtered.skills_matrix.filter(s => s.sector_name === selectedSector)
            };
        }

        // Filter by region (if needed for chart data)
        if (selectedRegion !== 'All Regions') {
            filtered = {
                skills_matrix: filtered.skills_matrix.map(sector => {
                    return {
                        ...sector,
                        regional_breakdown: sector.regional_breakdown.filter(
                            r => r.province === selectedRegion
                        )
                    };
                }).filter(sector => sector.regional_breakdown.length > 0)
            };
        }

        // Update chart with filtered data
        const chartData = buildChartData(filtered);
        renderChart(chartData.labels, chartData.demand, chartData.supply);
        
        // Update insights and actions
        if (filtered.skills_matrix.length > 0) {
            buildInsightCards(filtered);
            buildRecommendedActions(filtered);
        }

        // Update KPIs
        updateKPIs(filtered);
    }

    // ============================================
    // 13. SETUP EVENT LISTENERS
    // ============================================
    function setupEventListeners() {
        // Apply filters button
        const applyBtn = document.getElementById('applyFilters');
        if (applyBtn) {
            applyBtn.addEventListener('click', function(e) {
                e.preventDefault();
                applyFilters();
            });
        }

        // Auto-apply on dropdown change
        document.querySelectorAll('.filter-select').forEach(select => {
            select.addEventListener('change', function() {
                // Auto-apply after 500ms delay
                clearTimeout(window.filterTimeout);
                window.filterTimeout = setTimeout(applyFilters, 300);
            });
        });

        // Search functionality
        const searchInput = document.querySelector('.nav-search');
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const query = e.target.value.toLowerCase().trim();
                if (query.length > 2) {
                    highlightSearchResults(query);
                } else {
                    clearSearchHighlights();
                }
            });
        }
    }

    function highlightSearchResults(query) {
        document.querySelectorAll('.insight-text, .action-text').forEach(el => {
            const text = el.textContent.toLowerCase();
            const parent = el.closest('.insight-card') || el.closest('.action-item');
            if (text.includes(query)) {
                if (parent) {
                    parent.style.background = '#FDF6E8';
                    parent.style.borderColor = '#CAA84F';
                }
            } else {
                if (parent) {
                    parent.style.background = '';
                    parent.style.borderColor = '';
                }
            }
        });
    }

    function clearSearchHighlights() {
        document.querySelectorAll('.insight-card, .action-item').forEach(el => {
            el.style.background = '';
            el.style.borderColor = '';
        });
    }

    // ============================================
    // 14. INITIALIZE DASHBOARD
    // ============================================
    function init() {
        console.log('🚀 Initializing SkillMap Zimbabwe Dashboard...');
        console.log('📅 ' + new Date().toLocaleDateString());
        
        setupEventListeners();
        loadData();
    }

    // Start the dashboard
    init();

    console.log('📄 Dashboard script loaded');
});
