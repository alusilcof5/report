
        let salesData = [];

        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        }

        function formatNumber(value) {
            return new Intl.NumberFormat('en-US').format(value);
        }

        document.getElementById('csvFile').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                document.getElementById('loading').style.display = 'flex';
                
                Papa.parse(file, {
                    header: true,
                    dynamicTyping: true,
                    skipEmptyLines: true,
                    complete: function(results) {
                        salesData = results.data;
                        processData();
                        document.getElementById('loading').style.display = 'none';
                    },
                    error: function(error) {
                        console.error('Error parsing CSV:', error);
                        alert('Error processing CSV file');
                        document.getElementById('loading').style.display = 'none';
                    }
                });
            }
        });

        function processData() {
            if (salesData.length === 0) return;
            
            const cleanData = salesData.map(row => ({
                date: row.Date,
                month: row.Month,
                year: row.Year,
                salesAmount: parseFloat(row['Sales Amount']) || 0,
                channel: (row.Channel || '').trim(),
                category: (row.Category || '').trim(),
                region: (row['Country-Region'] || '').trim(),
                city: (row.City || '').trim()
            })).filter(row => row.salesAmount > 0);

            showStats(cleanData);
            createEvolutionChart(cleanData);
            createCategoryChart(cleanData);
            createRegionChart(cleanData);
            createChannelChart(cleanData);
            
            document.getElementById('stats').style.display = 'grid';
            document.getElementById('evolucion-ventas').style.display = 'block';
            document.getElementById('ventas-categoria').style.display = 'block';
            document.getElementById('ventas-region').style.display = 'block';
            document.getElementById('ventas-canal').style.display = 'block';
        }

        function showStats(data) {
            const totalSales = data.reduce((sum, row) => sum + row.salesAmount, 0);
            const totalOrders = data.length;
            const avgOrderValue = totalSales / totalOrders;
            const uniqueProducts = new Set(data.map(row => row.category)).size;
            
            const statsHtml = `
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">💰</div>
                    </div>
                    <div class="stat-value">${formatCurrency(totalSales)}</div>
                    <div class="stat-label">Total Revenue</div>
                    <div class="metric-change positive">
                        <span class="metric-arrow">↗</span>
                        <span class="metric-percentage">+12.5%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">📦</div>
                    </div>
                    <div class="stat-value">${formatNumber(totalOrders)}</div>
                    <div class="stat-label">Total Orders</div>
                    <div class="metric-change positive">
                        <span class="metric-arrow">↗</span>
                        <span class="metric-percentage">+8.3%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">⚡</div>
                    </div>
                    <div class="stat-value">${formatCurrency(avgOrderValue)}</div>
                    <div class="stat-label">Average Order Value</div>
                    <div class="metric-change positive">
                        <span class="metric-arrow">↗</span>
                        <span class="metric-percentage">+4.2%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">🎯</div>
                    </div>
                    <div class="stat-value">${uniqueProducts}</div>
                    <div class="stat-label">Product Categories</div>
                    <div class="metric-change positive">
                        <span class="metric-arrow">↗</span>
                        <span class="metric-percentage">+2.1%</span>
                    </div>
                </div>
            `;
            
            document.getElementById('stats').innerHTML = statsHtml;
        }

        function createEvolutionChart(data) {
            const monthlyData = {};
            
            data.forEach(row => {
                const key = `${row.year}-${row.month.toString().padStart(2, '0')}`;
                if (!monthlyData[key]) {
                    monthlyData[key] = 0;
                }
                monthlyData[key] += row.salesAmount;
            });
            
            const sortedMonths = Object.keys(monthlyData).sort();
            const values = sortedMonths.map(month => monthlyData[month]);
            
            const trace = {
                x: sortedMonths,
                y: values,
                type: 'scatter',
                mode: 'lines+markers',
                line: {
                    color: '#6366f1',
                    width: 3,
                    shape: 'spline'
                },
                marker: {
                    size: 8,
                    color: '#6366f1',
                    line: {
                        color: '#ffffff',
                        width: 2
                    }
                },
                fill: 'tonexty',
                fillcolor: 'rgba(99, 102, 241, 0.1)',
                name: 'Revenue',
                hovertemplate: '<b>%{x}</b><br>Revenue: %{y:$,.0f}<extra></extra>'
            };
            
            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#ffffff', family: 'Inter', size: 12 },
                xaxis: {
                    title: 'Period',
                    gridcolor: '#333338',
                    linecolor: '#333338',
                    tickcolor: '#333338'
                },
                yaxis: {
                    title: 'Revenue ($)',
                    gridcolor: '#333338',
                    linecolor: '#333338',
                    tickcolor: '#333338',
                    tickformat: '$,.0f'
                },
                hovermode: 'x unified',
                showlegend: false,
                margin: { t: 20, r: 20, b: 60, l: 80 }
            };
            
            Plotly.newPlot('evolucion-ventas', [trace], layout, {responsive: true, displayModeBar: false});
        }

        function createCategoryChart(data) {
            const categoryData = {};
            
            data.forEach(row => {
                if (row.category) {
                    if (!categoryData[row.category]) {
                        categoryData[row.category] = 0;
                    }
                    categoryData[row.category] += row.salesAmount;
                }
            });
            
            const sortedCategories = Object.entries(categoryData)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 10);
            
            const categories = sortedCategories.map(([cat, sales]) => cat);
            const values = sortedCategories.map(([cat, sales]) => sales);
            
            const trace = {
                x: values,
                y: categories,
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: '#6366f1',
                    line: {
                        color: '#8b5cf6',
                        width: 1
                    }
                },
                hovertemplate: '<b>%{y}</b><br>Revenue: %{x:$,.0f}<extra></extra>'
            };
            
            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#ffffff', family: 'Inter', size: 12 },
                xaxis: {
                    title: 'Revenue ($)',
                    gridcolor: '#333338',
                    linecolor: '#333338',
                    tickcolor: '#333338',
                    tickformat: '$,.0s'
                },
                yaxis: {
                    title: '',
                    automargin: true,
                    gridcolor: 'transparent',
                    linecolor: '#333338',
                    tickcolor: '#333338'
                },
                showlegend: false,
                margin: { t: 20, r: 20, b: 60, l: 150 }
            };
            
            Plotly.newPlot('ventas-categoria', [trace], layout, {responsive: true, displayModeBar: false});
        }

        function createRegionChart(data) {
            const regionData = {};
            
            data.forEach(row => {
                if (row.region) {
                    if (!regionData[row.region]) {
                        regionData[row.region] = 0;
                    }
                    regionData[row.region] += row.salesAmount;
                }
            });
            
            const sortedRegions = Object.entries(regionData)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 12);
            
            const regions = sortedRegions.map(([region, sales]) => region);
            const values = sortedRegions.map(([region, sales]) => sales);
            
            const trace = {
                x: regions,
                y: values,
                type: 'bar',
                marker: {
                    color: values,
                    colorscale: [
                        [0, '#6366f1'],
                        [0.5, '#8b5cf6'],
                        [1, '#a855f7']
                    ],
                    line: {
                        color: '#ffffff',
                        width: 1
                    }
                },
                hovertemplate: '<b>%{x}</b><br>Revenue: %{y:$,.0f}<extra></extra>'
            };
            
            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#ffffff', family: 'Inter', size: 12 },
                xaxis: {
                    title: 'Regions',
                    tickangle: -45,
                    gridcolor: 'transparent',
                    linecolor: '#333338',
                    tickcolor: '#333338'
                },
                yaxis: {
                    title: 'Revenue ($)',
                    gridcolor: '#333338',
                    linecolor: '#333338',
                    tickcolor: '#333338',
                    tickformat: '$,.0s'
                },
                showlegend: false,
                margin: { t: 20, r: 20, b: 120, l: 80 }
            };
            
            Plotly.newPlot('ventas-region', [trace], layout, {responsive: true, displayModeBar: false});
        }

        function createChannelChart(data) {
            const channelData = {};
            
            data.forEach(row => {
                if (row.channel) {
                    if (!channelData[row.channel]) {
                        channelData[row.channel] = 0;
                    }
                    channelData[row.channel] += row.salesAmount;
                }
            });
            
            const channels = Object.keys(channelData);
            const values = Object.values(channelData);
            
            const trace = {
                labels: channels,
                values: values,
                type: 'pie',
                hole: 0.5,
                marker: {
                    colors: ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe', '#e9d5ff'],
                    line: {
                        color: '#1a1a1b',
                        width: 2
                    }
                },
                textinfo: 'label+percent',
                textfont: {
                    color: '#ffffff',
                    family: 'Inter',
                    size: 12
                },
                hovertemplate: '<b>%{label}</b><br>Revenue: %{value:$,.0f}<br>Share: %{percent}<extra></extra>'
            };
            
            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#ffffff', family: 'Inter', size: 12 },
                showlegend: true,
                legend: {
                    orientation: 'h',
                    x: 0.5,
                    xanchor: 'center',
                    y: -0.1
                },
                margin: { t: 20, r: 20, b: 80, l: 20 }
            };
            
            Plotly.newPlot('ventas-canal', [trace], layout, {responsive: true, displayModeBar: false});
        }
    