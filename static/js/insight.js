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
        return duration;
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
    return `${hrs} hours ${mins} minutes`;
}

function hexToRgba(hex, alpha = 1) {
    const [r, g, b] = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i).slice(1).map(n => parseInt(n, 16));
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
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
    const canvas = document.getElementById('passionChart');
    const ctx = document.getElementById('passionChart').getContext('2d');

    if (passionChartInstance) {
        passionChartInstance.destroy();
    }

    fetch(`/yearly-passion-progress-data/${currentYear}/`)
        .then(response => response.json())
        .then(data => {

            if (!data.weekly_passion_data.some(week => Object.keys(week.passions).length > 0)) {
                // Edge-case where there is no passion activity for the entire year.
                ctx.clearRect(0, 0, ctx.canvas.clientWidth, ctx.canvas.clientHeight);

                ctx.font = '20px Arial';
                ctx.fillStyle = 'black';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                ctx.fillText("No Data Available", canvas.width / 2, canvas.height / 2);
                return;
            }

            const labels = data.weekly_passion_data.map(week => formatWeekRange(week.date_range));
            const datasets = [];
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

            for (const [passionName, passionData] of Object.entries(passionDataset)) {
                datasets.push(createDataset(passionName, passionData.data, passionData.color));
            }

            const chartConfig = {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 24
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