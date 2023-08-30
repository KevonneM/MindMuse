// year vars for event functions
var currentYear = null;
var accountCreationYear = null;
var chevronLeft = null;
var chevronRight = null;
let yearTitle = null;
var myEventChart;

// year vars for task functions
var currentYearTasks = null;
var accountCreationYearTasks = null;
var chevronLeftTasks = null;
var chevronRightTasks = null;
let yearTitleTasks = null;

// year vars for passion functions
var currentYearPassions = null;
var accountCreationYearPassions = null;
var chevronLeftPassions = null;
var chevronRightPassions = null;
let yearTitlePassions = null;
var passionChartInstance = null;
var categoryChartInstance = null;

function updateEventsChart() {
    const isDailyTabActive = document.getElementById('daily-events-tab').classList.contains('active');
    const isWeeklyTabActive = document.getElementById('weekly-events-tab').classList.contains('active');
    const isMonthlyTabActive = document.getElementById('monthly-events-tab').classList.contains('active');

    let ctx;
    let maxEventValue;
    let maxEventIndex;

    yearTitle.textContent = currentYear;

    chevronLeft.classList.toggle("disabled", currentYear <= accountCreationYear);
    chevronRight.classList.toggle("disabled", currentYear >= new Date().getFullYear());

    fetch(`/yearly_event_data/${currentYear}`)
    .then(response => response.json())
    .then(data => {
        document.querySelector('#daily-average').textContent = Number(data.daily_average).toFixed(2);
        document.querySelector('#weekly-average').textContent = Number(data.weekly_average).toFixed(2);
        document.querySelector('#monthly-average').textContent = Number(data.monthly_average).toFixed(2);

        if (myEventChart) {
            myEventChart.destroy();
        }

        if (isDailyTabActive) {
            ctx = document.getElementById('dailyEventsChart').getContext('2d');

            maxEventValue = Math.max(...data.daily_event_data);
            maxEventIndex = data.daily_event_data.indexOf(maxEventValue);

            var date = new Date(currentYear, 0);
            date.setDate(maxEventIndex + 1);
            var dateString = date.toLocaleDateString();

            document.querySelector('#busiest-day').textContent = `Busiest Day: ${dateString} : Events: ${maxEventValue}`;

            let pointBackgroundColorsZero = [];
            let pointBackgroundColorsNonZero = [];
            let dataZero = [];
            let dataNonZero = [];

            data.daily_event_data.forEach((value, index) => {
                let pointData = { x: index + 1, y: value };

                if (value === 0) {
                    dataZero.push(pointData);
                    pointBackgroundColorsZero.push(index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)');
                } else {
                    dataNonZero.push(pointData);
                    pointBackgroundColorsNonZero.push(index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)');
                }
            });

            myEventChart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Days with zero events',
                        data: dataZero,
                        pointBackgroundColor: pointBackgroundColorsZero,
                        pointRadius: 5,
                    }, {
                        label: 'Days with non-zero events',
                        data: dataNonZero,
                        pointBackgroundColor: pointBackgroundColorsNonZero,
                        pointRadius: 5,
                    }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    var date = new Date(currentYear, 0);
                                    date.setDate(context.parsed.x);
                                    var dateString = date.toLocaleDateString();

                                    var events = context.parsed.y;

                                    return dateString + ': ' + 'Events: ' + events;
                                }
                            }
                        },
                        legend: {
                            display: true,
                        }
                    },
                    scales: {
                        x: {
                            type: 'linear',
                            title: {
                                display: true,
                                text: 'Day of the year'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of events'
                            }
                        }
                    }
                }
            });

        } else if (isWeeklyTabActive) {
            ctx = document.getElementById('weeklyEventsChart').getContext('2d');

            let weeklyEventCounts = data.weekly_event_data.map(weekData => weekData[0]);
            maxEventValue = Math.max(...weeklyEventCounts);
            maxEventIndex = weeklyEventCounts.indexOf(maxEventValue);

            document.querySelector('#busiest-week').textContent = `Busiest Week: ${maxEventIndex+1} : Events: ${maxEventValue}`;

            let pointBackgroundColors = weeklyEventCounts.map((value, index) =>
                index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)'
            );

            myEventChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: weeklyEventCounts.map((_, index) => `Week ${index+1}`),
                    datasets: [{
                        label: 'Number of events',
                        data: weeklyEventCounts,
                        backgroundColor: pointBackgroundColors,
                    }],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of events'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function(tooltipItem) {
                                    var weekData = data.weekly_event_data[tooltipItem[0].dataIndex];
                                    var startDate = weekData[1];
                                    var endDate = weekData[2];
                                    return `${startDate} - ${endDate}`;
                                },
                                label: function(tooltipItem) {
                                    var events = tooltipItem.raw;
                                    return 'Events: ' + events;
                                }
                            }
                        },
                        legend: {
                            display: true,
                        }
                    }
                }
            });

        } else if (isMonthlyTabActive) {
            ctx = document.getElementById('monthlyEventsChart').getContext('2d');

            maxEventValue = Math.max(...data.monthly_event_data);
            maxEventIndex = data.monthly_event_data.indexOf(maxEventValue);

            var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"];
            var monthString = monthNames[maxEventIndex];

            document.querySelector('#busiest-month').textContent = `Busiest Month: ${monthString} : Events: ${maxEventValue}`;

            let pointBackgroundColors = new Array(12).fill('rgba(0, 123, 255, 0.5)');
            pointBackgroundColors[maxEventIndex] = 'rgba(255, 0, 0, 0.5)';

            myEventChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: monthNames,
                    datasets: [{
                        label: 'Number of events',
                        data: data.monthly_event_data,
                        backgroundColor: pointBackgroundColors,
                    }],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of events'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                        }
                    }
                }
            });
        }
    });
}

function initEventInsights(year, accountYear) {
    currentYear = year;
    accountCreationYear = accountYear;

    console.log("initEventInsights called with year: ", year, ", accountYear: ", accountYear);

    chevronLeft = document.getElementById("prev-year");
    chevronRight = document.getElementById("next-year");
    yearTitle = document.querySelector(".card-title");

    chevronLeft.addEventListener("click", function() {
        if (currentYear > accountCreationYear) {
            currentYear--;
            updateEventsChart();
        }
    });

    chevronRight.addEventListener("click", function() {
        if (currentYear < new Date().getFullYear()) {
            currentYear++;
            updateEventsChart();
        }
    });

    document.getElementById('daily-events-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(updateEventsChart, 1000);
    });

    document.getElementById('weekly-events-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(updateEventsChart, 1000);
    });

    document.getElementById('monthly-events-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(updateEventsChart, 1000);
    });
    
    updateEventsChart();
}

// Task Insight js

var dailyTasksChart = null;
var weeklyTasksChart = null;
var monthlyTasksChart = null;

function computeAverageCompletionRate(data) {
    
    const validEntries = data.filter(entry => entry.total_tasks > 0);

    const sumCompletionRate = validEntries.reduce((sum, entry) => sum + entry.completion_rate, 0);

    return validEntries.length ? sumCompletionRate / validEntries.length : 0;
}

function parseLocalDate(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
}

function updateTaskCharts(year) {
    const monthNames = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"];

    yearTitleTasks.textContent = currentYearTasks;

    chevronLeftTasks.classList.toggle("disabled", currentYearTasks <= accountCreationYearTasks);
    chevronRightTasks.classList.toggle("disabled", currentYearTasks >= new Date().getFullYear());

    fetch(`/yearly-task-completion-data/${year}`)
        .then(response => response.json())
        .then(data => {
            const dailyTaskData = data.daily_task_data;
            const weeklyTaskData = data.weekly_task_data;
            const monthlyTaskData = data.monthly_task_data;

            const dailyAverageCompletionRate = computeAverageCompletionRate(dailyTaskData);
            const weeklyAverageCompletionRate = computeAverageCompletionRate(weeklyTaskData);
            const monthlyAverageCompletionRate = computeAverageCompletionRate(monthlyTaskData);

            document.getElementById('daily-task-average').textContent = `${dailyAverageCompletionRate.toFixed(2)}%`;
            document.getElementById('weekly-task-average').textContent = `${weeklyAverageCompletionRate.toFixed(2)}%`;
            document.getElementById('monthly-task-average').textContent = `${monthlyAverageCompletionRate.toFixed(2)}%`;

            const dailyLabels = dailyTaskData.map(entry => {
                const dateObj = parseLocalDate(entry.date);
                const month = monthNames[dateObj.getMonth()];
                const day = dateObj.getDate();
                return `${month} ${day}`;
            });
            const weeklyLabels = weeklyTaskData.map(entry => {
                const dateParts = entry.date.split(" - ");
                const startObj = parseLocalDate(dateParts[0]);
                const endObj = parseLocalDate(dateParts[1]);

                const startMonth = monthNames[startObj.getMonth()];
                const startDay = startObj.getDate();
                const endMonth = monthNames[endObj.getMonth()];
                const endDay = endObj.getDate();
                
                return `${startMonth} ${startDay} - ${endMonth} ${endDay}`;
            });
            const monthlyLabels = monthlyTaskData.map(entry => entry.month);

            const chartData = {
                daily: {ctx: 'dailyTasksChart', labels: dailyLabels, data: dailyTaskData, chart: dailyTasksChart},
                weekly: {ctx: 'weeklyTasksChart', labels: weeklyLabels, data: weeklyTaskData, chart: weeklyTasksChart},
                monthly: {ctx: 'monthlyTasksChart', labels: monthlyLabels, data: monthlyTaskData, chart: monthlyTasksChart},
            };

            Object.values(chartData).forEach(({ctx, labels, data, chart}) => {
                const canvas = document.getElementById(ctx);
                const canvasContext = document.getElementById(ctx).getContext('2d');
                const chartType = ctx.replace('TasksChart', '').toLowerCase();

                if (chart) {
                    chart.destroy();
                }

                const completionRateData = data.map(entry => entry.completion_rate);
                chart = new Chart(canvasContext, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Completion Rate',
                            data: completionRateData,
                            backgroundColor: 'rgba(0, 123, 255, 0.5)',
                            borderColor: 'rgba(0, 123, 255, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: function(context) {
                                        const dateStr = context[0].label;
                                        
                                        switch (chartType) {
                                            case 'daily': {
                                                return dateStr;
                                            }
                                            case 'weekly': {
                                                return dateStr;
                                            }
                                            case 'monthly': {
                                                return dateStr;
                                            }
                                            default:
                                                return dateStr;
                                        }
                                    },
                                    label: function(context) {
                                        const index = context.dataIndex;
                                        const entry = data[index];
                                        return [
                                            `Completion Rate: ${entry.completion_rate.toFixed(2)}%`,
                                            `Ratio: ${entry.ratio}`,
                                            `Total Tasks: ${entry.total_tasks}`,
                                            `Completed: ${entry.completed}`,
                                            `Incompleted: ${entry.incompleted}`
                                        ];
                                    }
                                }
                            }
                        }
                    }
                });

                // Update the global chart variables
                if(ctx == 'dailyTasksChart'){
                    dailyTasksChart = chart;
                }else if(ctx == 'weeklyTasksChart'){
                    weeklyTasksChart = chart;
                }else if(ctx == 'monthlyTasksChart'){
                    monthlyTasksChart = chart;
                }
            });
        });
}

function initTaskCompletionInsights(year, accountYear) {
    currentYearTasks = year;
    accountCreationYearTasks = accountYear

    console.log("initTaskCompletionInsights called with year: ", year, ", accountYear: ", accountYear);

    chevronLeftTasks = document.getElementById('prev-year-tasks');
    chevronRightTasks = document.getElementById('next-year-tasks');
    yearTitleTasks = document.querySelector('.card-title-task');

    yearTitleTasks.textContent = currentYearTasks;

    const updateChart = () => {
        if (document.getElementById('daily-task-tab').classList.contains('active')) {
            updateTaskCharts(currentYearTasks, 'daily');
        } else if (document.getElementById('weekly-task-tab').classList.contains('active')) {
            updateTaskCharts(currentYearTasks, 'weekly');
        } else if (document.getElementById('monthly-task-tab').classList.contains('active')) {
            updateTaskCharts(currentYearTasks, 'monthly');
        }
    };

    chevronLeftTasks.addEventListener('click', () => {
        if (currentYearTasks > accountCreationYearTasks) {
            currentYearTasks--;
            yearTitleTasks.textContent = currentYearTasks;
            updateChart();
        }
    });

    chevronRightTasks.addEventListener('click', () => {
        if (currentYearTasks < new Date().getFullYear()) {
            currentYearTasks++;
            yearTitleTasks.textContent = currentYearTasks;
            updateChart();
        }
    });

    document.getElementById('daily-task-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    document.getElementById('weekly-task-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    document.getElementById('monthly-task-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    updateChart();
}

// Passion Insight js

// seperate helper function to formate date range for passion chart.
function formatWeekRange(weekRange) {
    const monthNames = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"];
                        
    const [startDateStr, endDateStr] = weekRange.split(" - ");
    const startObj = parseLocalDate(startDateStr);
    const endObj = parseLocalDate(endDateStr);
    
    const startMonth = monthNames[startObj.getMonth()];
    const startDay = startObj.getDate();
    const endMonth = monthNames[endObj.getMonth()];
    const endDay = endObj.getDate();
    
    return `${startMonth} ${startDay} - ${endMonth} ${endDay}`;
}


// Helper function to convert the duration string to hours for plotting.
function durationToHours(duration) {
    if (typeof duration === "string") {
        const match = duration.match(/P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
        const hours = match[2] ? parseInt(match[2]) : 0;
        const minutes = match[3] ? parseInt(match[3]) : 0;
        return hours + (minutes / 60);
    } else if (typeof duration === "number") {
        const hours = Math.floor(duration);
        const minutes = Math.round((duration - hours) * 60);
        return { hours, minutes };
    } else {
        console.error("Unexpected duration type:", typeof duration, duration);
        return 0;
    }
}

// Helper function to convert the hours to duration for displaying appropriate values to users.
function hoursToDuration(hours) {
    const totalMinutes = hours * 60;
    const hrs = Math.floor(totalMinutes / 60);
    const mins = Math.round(totalMinutes % 60);
    return `${hrs} hrs ${mins} mins`;
}

function hexToRgba(hex, alpha = 1) {
    const [r, g, b] = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i).slice(1).map(n => parseInt(n, 16));
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function darkenRgbaColor(rgba, amountToDarken) {
    const rgbaValues = rgba.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
    const r = Math.max(parseInt(rgbaValues[1]) - amountToDarken, 0);
    const g = Math.max(parseInt(rgbaValues[2]) - amountToDarken, 0);
    const b = Math.max(parseInt(rgbaValues[3]) - amountToDarken, 0);
    const a = parseFloat(rgbaValues[4]);
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}

// Helper function to create a dataset for Chart.js
function createDataset(name, data, color) {
    return {
        label: name,
        data: data,
        borderColor: hexToRgba(color, 1),
        backgroundColor: hexToRgba(color, 0.2),
        borderWidth: 2,
        fill: true
    };
}

// Main functions to initialize the chart
function updatePassionInsightsChart(currentYear) {
    const ctx = document.getElementById('passionChart').getContext('2d');

    if (passionChartInstance) {
        passionChartInstance.destroy();
    }

    yearTitlePassions.textContent = currentYear;

    chevronLeftPassions.classList.toggle("disabled", currentYear <= accountCreationYearPassions);
    chevronRightPassions.classList.toggle("disabled", currentYear >= new Date().getFullYear());

    fetch(`/yearly-passion-progress-data/${currentYear}/`)
        .then(response => response.json())
        .then(data => {
            let labels, datasets;

            if (!data.weekly_passion_data.some(week => Object.keys(week.passions).length > 0)) {
                // Edge-case where there is no passion activity for the entire year.
                labels = Array(52).fill("").map((_, i) => `Week ${i + 1}`);
                datasets = [{
                    label: "No Passion Data",
                    data: Array(52).fill(0),
                    backgroundColor: '#808080',
                    borderColor: '#808080',
                    fill: false,
                }];
            } else {
                labels = data.weekly_passion_data.map(week => formatWeekRange(week.date_range));
                const passionDataset = {};
                const defaultColor = "#808080";

                for (const week of data.weekly_passion_data) {
                    for (const passionName in week.passions) {
                        if (!passionDataset[passionName]) {
                            passionDataset[passionName] = {
                                'data': Array(data.weekly_passion_data.length).fill(0), // initialize all weeks to 0
                                'color': week.passions[passionName].color || defaultColor
                            };
                        }
                        passionDataset[passionName].data[data.weekly_passion_data.indexOf(week)] = durationToHours(week.passions[passionName].duration);
                    }
                }

                datasets = [];
                for (const [passionName, passionData] of Object.entries(passionDataset)) {
                    datasets.push(createDataset(passionName, passionData.data, passionData.color));
                }
            }

            const chartConfig = {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 24,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const passionName = context.dataset.label;
                                    const value = context.parsed.y;
                                    const formattedDuration = hoursToDuration(value);
                                    return `${passionName}: ${formattedDuration}`;
                                }
                            }
                        }
                    }
                }
            };

            passionChartInstance = new Chart(ctx, chartConfig);
        })
        .catch(error => {
            console.error("Error fetching passion data:", error);
        });
}

function initCategoryChart(currentYear) {
    const ctx = document.getElementById('categoriesChart').getContext('2d');

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    const baseCategoryColors = {
        'Physical': '#614280',
        'Mental': '#614280',
        'Spiritual': '#614280'
    };

    const getDynamicHexColor = (i) => `#${(i * 15 % 255).toString(16).padStart(2, '0')}${((i + 5) * 20 % 255).toString(16).padStart(2, '0')}${((i + 3) * 25 % 255).toString(16).padStart(2, '0')}`;

    fetch(`/yearly-passion-progress-data/${currentYear}/`)
        .then(response => response.json())
        .then(data => {
            const aggregatedCategoryData = {};

            for (const week of data.weekly_passion_data) {
                for (const categoryName in week.categories) {
                    if (!aggregatedCategoryData[categoryName]) {
                        aggregatedCategoryData[categoryName] = {
                            totalDuration: 0,
                            passions: {}
                        };
                    }
                    
                    aggregatedCategoryData[categoryName].totalDuration += durationToHours(week.categories[categoryName]);
            
                    for (const passionName in week.passions) {
                        // Only consider this passion if it belongs to the current category
                        if (week.passions[passionName].category === categoryName) {
                            if (!aggregatedCategoryData[categoryName].passions[passionName]) {
                                aggregatedCategoryData[categoryName].passions[passionName] = {
                                    duration: 0,
                                    category: categoryName
                                };
                            }
                            aggregatedCategoryData[categoryName].passions[passionName].duration += durationToHours(week.passions[passionName].duration);
                        }
                    }
                }
            }            
            
            const labels = Object.keys(aggregatedCategoryData);
            const translucentAlpha = 0.5;
            const colors = labels.map((label, i) => hexToRgba(baseCategoryColors[label] || getDynamicHexColor(i), translucentAlpha));
            const borderColors = colors.map(color => darkenRgbaColor(color, 80));
            const datasets = [{
                label: labels,
                data: Object.values(aggregatedCategoryData).map(category => durationToHours(category.totalDuration)),
                backgroundColor: colors,
                borderColor: borderColors,
                borderWidth: 2
            }];

            const chartConfig = {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            barPercentage: 0.7,
                            categoryPercentage: 0.9
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {
                                        return data.labels.map((label, i) => {
                                            const meta = chart.getDatasetMeta(0);
                                            const ds = data.datasets[0];
                                            const arc = meta.data[i];
                                            const custom = arc && arc.custom || {};
                                            const fill = custom.backgroundColor ? custom.backgroundColor : ds.backgroundColor[i];
                                            const stroke = custom.borderColor ? custom.borderColor : ds.borderColor[i];
                                            const bw = custom.borderWidth ? custom.borderWidth : ds.borderWidth[i];
                        
                                            return {
                                                text: label,
                                                fillStyle: fill,
                                                strokeStyle: stroke,
                                                lineWidth: bw,
                                                index: i
                                            };
                                        });
                                    } else {
                                        return [];
                                    }
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const category = context.label;
                                    const totalDuration = aggregatedCategoryData[category].totalDuration;
                                    const formattedDuration = hoursToDuration(totalDuration);
                            
                                    const passions = aggregatedCategoryData[category].passions;
                                    let passionsArray = [];
                            
                                    for (const passion in passions) {
                                        const passionDuration = passions[passion].duration;
                                        
                                        if (typeof passionDuration !== 'number' || isNaN(passionDuration)) {
                                            console.error(`Invalid duration for passion ${passion}:`, passionDuration);
                                            continue;
                                        }
                            
                                        if (totalDuration > 0) {
                                            const percent = (passionDuration / totalDuration) * 100;
                                            passionsArray.push(`${passion}: ${hoursToDuration(passionDuration)} (${percent.toFixed(2)}%)`);
                                        } else {
                                            passionsArray.push(`${passion}: ${hoursToDuration(passionDuration)} (0%)`);
                                        }
                                    }
                            
                                    return [`${category}: ${formattedDuration}`].concat(passionsArray);
                                }
                            }                            
                        }                                               
                    }
                }
            };

            categoryChartInstance = new Chart(ctx, chartConfig);
        })
        .catch(error => {
            console.error("Error fetching category data:", error);
        });
}

function initPassionInsights(currentYear, accountCreationYear) {
    currentYearPassions = currentYear;
    accountCreationYearPassions = accountCreationYear;

    console.log("initPassionInsights called with year: ", currentYear, ", accountCreationYear: ", accountCreationYear);

    chevronLeftPassions = document.getElementById('prev-year-passions');
    chevronRightPassions = document.getElementById('next-year-passions');
    yearTitlePassions = document.querySelector('.card-title-passion');

    yearTitlePassions.textContent = currentYearPassions;

    const updateChart = () => {
        if (document.getElementById('passion-tab').classList.contains('active')) {
            updatePassionInsightsChart(currentYearPassions);
        } else if (document.getElementById('category-tab').classList.contains('active')) {
            initCategoryChart(currentYearPassions);
        }
    };

    chevronLeftPassions.addEventListener('click', () => {
        if (currentYearPassions > accountCreationYearPassions) {
            currentYearPassions--;
            yearTitlePassions.textContent = currentYearPassions;
            updateChart();
        }
    });

    chevronRightPassions.addEventListener('click', () => {
        if (currentYearPassions < new Date().getFullYear()) {
            currentYearPassions++;
            yearTitlePassions.textContent = currentYearPassions;
            updateChart();
        }
    });

    document.getElementById('passion-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    document.getElementById('category-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    updateChart();
}

// Insight Overview js

// Helper function to to find current week for event overview.
function formatDateToYYYYMMDD(dateObj) {
    const year = dateObj.getUTCFullYear();
    const month = (dateObj.getUTCMonth() + 1).toString().padStart(2, '0');
    const day = dateObj.getUTCDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function findWeekByDate(targetDate, weeklyEventData) {
    const targetDateString = formatDateToYYYYMMDD(targetDate);

    for (const week of weeklyEventData) {
        let startDateString = week[1];
        let endDateString = week[2];

        if (targetDateString >= startDateString && targetDateString <= endDateString) {
            return week;
        }
    }

    console.error("Week not found!");
    return null;
}

function stripTimeFromDate(dateObj) {
    return new Date(Date.UTC(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()));
}

async function updateInsightOverview(year) {
    currentDate = stripTimeFromDate(new Date());
    const currentYear = new Date().getFullYear();
    const currentMonthIndex = new Date().getMonth();
    const prevMonthIndex = currentMonthIndex === 0 ? 11 : currentMonthIndex - 1;
    try {
        // Fetch and handle task data.
        const taskResponse = await fetch(`/yearly-task-completion-data/${year}`);
        if (taskResponse.status !== 200) {
            throw new Error("Failed to fetch Task Overview data");
        }
        const taskData = await taskResponse.json();
        
        // Aquire and manipulate latest and previous task data.
        const dailyLastData = taskData.daily_task_data[taskData.daily_task_data.length - 1];
        const dailyPrevData = taskData.daily_task_data[taskData.daily_task_data.length - 2] || { completion_rate: 0 };

        const weeklyLastData = taskData.weekly_task_data[taskData.weekly_task_data.length - 1];
        const weeklyPrevData = taskData.weekly_task_data[taskData.weekly_task_data.length - 2] || { completion_rate: 0 };

        const monthlyLastData = taskData.monthly_task_data.find(monthData => new Date(monthData.month + " 1 " + currentYear).getMonth() === currentMonthIndex);
        const monthlyPrevData = taskData.monthly_task_data.find(monthData => new Date(monthData.month + " 1 " + currentYear).getMonth() === prevMonthIndex);

        // Fetch and handle event data.
        const eventResponse = await fetch(`/yearly_event_data/${year}`);
        if (eventResponse.status !== 200) {
            throw new Error("Failed to fetch Event Overview data");
        }
        const eventData = await eventResponse.json();

        let currentWeek = findWeekByDate(currentDate, eventData.weekly_event_data);
        if (!currentWeek) {
            console.error("Current week data not found in eventData.weekly_event_data");
            return;
        }

        let currentIndex = eventData.weekly_event_data.indexOf(currentWeek);
        const currentWeekEvents = currentWeek[0];
        const previousWeekEvents = currentIndex > 0 ? eventData.weekly_event_data[currentIndex - 1][0] : 0;

        const eventDifference = currentWeekEvents - previousWeekEvents;
        const eventChangePercent = (previousWeekEvents === 0 && currentWeekEvents === 0) ? 0 :
        (previousWeekEvents === 0 ? 100 : (eventDifference / previousWeekEvents) * 100);
        let eventChangeTerm;
        
        if(eventChangePercent > 0) {
            eventChangeTerm = "increase";
        } else if(eventChangePercent < 0) {
            eventChangeTerm = "decrease";
        } else {
            eventChangeTerm = "change"; // If it's 0% change
        }

        // Fetch and handle passion data.
        const passionResponse = await fetch(`/yearly-passion-progress-data/${year}`);
        if (passionResponse.status !== 200) {
            throw new Error("Failed to fetch Passion Overview data");
        }
        const passionData = await passionResponse.json();

        // Acquire and manipulate passion data for the current week and the previous week.
        const currentWeekPassionData = passionData.weekly_passion_data[currentIndex];
        const previousWeekPassionData = passionData.weekly_passion_data[currentIndex - 1] || { passions: {} };
        
        const getTotalDuration = (weekData) => {
            let totalDuration = 0; 
            for (const passionName in weekData.passions) {
                totalDuration += weekData.passions[passionName].duration;
            }
            return totalDuration;
        }
        function passionDurationToHoursAndMinutes(duration) {
            if (typeof duration === "string") {
                const durations = duration.split('P').filter(Boolean); // Split the concatenated durations
                let totalHours = 0;
                for (const d of durations) {
                    const match = d.match(/(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
                    const hours = match[2] ? parseInt(match[2]) : 0;
                    const minutes = match[3] ? parseInt(match[3]) : 0;
                    totalHours += hours + (minutes / 60);
                }
                const roundedHours = Math.floor(totalHours);
                const minutes = Math.round((totalHours - roundedHours) * 60);
                return { hours: roundedHours, minutes: minutes };
            } else if (typeof duration === "number") {
                const hours = Math.floor(duration);
                const minutes = Math.round((duration - hours) * 60);
                return { hours, minutes };
            } else {
                console.error("Unexpected duration type:", typeof duration, duration);
                return { hours: 0, minutes: 0 };
            }
        }
        
        
        const currentWeekDuration = getTotalDuration(currentWeekPassionData);
        const previousWeekDuration = getTotalDuration(previousWeekPassionData);
        const currentWeekDurationObj = passionDurationToHoursAndMinutes(currentWeekDuration);
        const previousWeekDurationObj = passionDurationToHoursAndMinutes(previousWeekDuration);
        const currentWeekDurationFloat = currentWeekDurationObj.hours + (currentWeekDurationObj.minutes / 60);
        const previousWeekDurationFloat = previousWeekDurationObj.hours + (previousWeekDurationObj.minutes / 60);
        const passionDurationDifference = currentWeekDurationFloat - previousWeekDurationFloat;
        const passionDurationDifferenceObj = passionDurationToHoursAndMinutes(passionDurationDifference);

        let passionChangePercent;
        if (previousWeekDurationFloat === 0 && currentWeekDurationFloat === 0) {
            passionChangePercent = 0;
        } else if (previousWeekDurationFloat === 0) {
            passionChangePercent = 100;
        } else {
            passionChangePercent = (passionDurationDifference / previousWeekDurationFloat) * 100;
        }

        if(passionChangePercent > 0) {
            passionChangeTerm = "increase";
        } else if(passionChangePercent < 0) {
            passionChangeTerm = "decrease";
        } else {
            passionChangeTerm = "change"; // If it's 0% change
        }

        const slide = document.querySelector("#textCarousel #taskOverviewSlide");
        slide.innerHTML = `
            <h3>Task Overview</h3>
            <div class="d-flex justify-content-between">
                <div>
                    <h4>Daily</h4>
                    <p>Completion Rate: ${dailyLastData.completion_rate.toFixed(2)}%</p>
                    <p>Change: ${(dailyLastData.completion_rate - dailyPrevData.completion_rate).toFixed(2)}%</p>
                </div>
                <div>
                    <h4>Weekly</h4>
                    <p>Completion Rate: ${weeklyLastData.completion_rate.toFixed(2)}%</p>
                    <p>Change: ${(weeklyLastData.completion_rate - weeklyPrevData.completion_rate).toFixed(2)}%</p>
                </div>
                <div>
                    <h4>Monthly</h4>
                    <p>Completion Rate: ${monthlyLastData.completion_rate.toFixed(2)}%</p>
                    <p>Change: ${(monthlyLastData.completion_rate - monthlyPrevData.completion_rate).toFixed(2)}%</p>
                </div>
            </div>
        `;
        const slide2 = document.querySelector("#textCarousel #eventOverviewSlide");
        slide2.innerHTML = `
            <h3>Event Overview</h3>
            <p>Events attended this week: ${currentWeekEvents}</p>
            <p>Events attended last week: ${previousWeekEvents}</p>
            <p>${eventDifference} ${eventDifference > 0 ? 'More' : 'Less'} events attended than last week</p>
            <p>${eventChangePercent.toFixed(2)}% ${eventChangeTerm} from last week</p>
        `;
        const slide3 = document.querySelector("#textCarousel #passionOverviewSlide");
        slide3.innerHTML = `
            <h3>Passion Overview</h3>
            <p>Total time invested this week: ${currentWeekDurationObj.hours}h ${currentWeekDurationObj.minutes}m</p>
            <p>${Math.abs(passionDurationDifferenceObj.hours)}h ${Math.abs(passionDurationDifferenceObj.minutes)}m ${passionDurationDifference > 0 ? 'more' : 'less'} than last week</p>
            <p>${passionChangePercent.toFixed(2)}% ${passionChangeTerm} from last week</p>
        `;
    } catch (error) {
        console.error("Failed to update insight overview:", error);
    }
}