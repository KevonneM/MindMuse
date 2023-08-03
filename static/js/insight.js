// year vars for event functions
var currentYear = null;
var accountCreationYear = null;
var chevronLeft = null;
var chevronRight = null;
let yearTitle = null;

// year vars for task functions
var currentYearTasks = null;
var accountCreationYearTasks = null;
var chevronLeftTasks = null;
var chevronRightTasks = null;
let yearTitleTasks = null;



function eventUpdateYear() {
    console.log("currentYear: ", currentYear);
    console.log("accountCreationYear: ", accountCreationYear);
    var dailyTabActive = document.getElementById('daily-tab').classList.contains('active');
    if (!dailyTabActive) {
        return;
    }
    
    yearTitle.textContent = currentYear;
    console.log("Fetching data for year: ", currentYear);

    chevronLeft.classList.toggle("disabled", currentYear <= accountCreationYear);
    chevronRight.classList.toggle("disabled", currentYear >= new Date().getFullYear());

    fetch(`/yearly_event_data/${currentYear}`)
    .then(response => response.json())
    .then(data => {
        console.log("Received data: ", data);

        document.querySelector('#daily-average').textContent = Number(data.daily_average).toFixed(2);
        document.querySelector('#weekly-average').textContent = Number(data.weekly_average).toFixed(2);
        document.querySelector('#monthly-average').textContent = Number(data.monthly_average).toFixed(2);

        const ctx = document.getElementById('dailyEventsChart').getContext('2d');

        if (window.myChart) {
            window.myChart.destroy();
        }

        let maxEventValue = Math.max(...data.daily_event_data);
        let maxEventIndex = data.daily_event_data.indexOf(maxEventValue);

        var date = new Date(currentYear, 0);
        date.setDate(maxEventIndex + 1);
        var dateString = date.toLocaleDateString();

        document.querySelector('#busiest-day').textContent = `Busiest Day: ${dateString} : Events: ${maxEventValue}`;

        let pointBackgroundColorsZero = [];
        let pointBackgroundColorsNonZero = [];

        let dataZero = [];
        let dataNonZero = [];

        data.daily_event_data.forEach((value, index) => {
            let pointData = {x: index+1, y: value};

            if (value === 0) {
                dataZero.push(pointData);
                pointBackgroundColorsZero.push(index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)');
            } else {
                dataNonZero.push(pointData);
                pointBackgroundColorsNonZero.push(index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)');
            }
        });

        window.myChart = new Chart(ctx, {
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
                        title: {
                            display: true,
                            text: 'Number of events'
                        }
                    }
                }
            }
        });
    });
}

// Global variable to hold the Chart.js instance for the weekly chart.
var myWeeklyChart = null;

function eventUpdateWeek() {
    console.log("currentYear: ", currentYear);
    console.log("accountCreationYear: ", accountCreationYear);
    var weeklyTabActive = document.getElementById('weekly-tab').classList.contains('active');
    if (!weeklyTabActive) {
        return;
    }

    yearTitle.textContent = currentYear;
    console.log("Fetching data for week: ", currentYear);

    chevronLeft.classList.toggle("disabled", currentYear <= accountCreationYear);
    chevronRight.classList.toggle("disabled", currentYear >= new Date().getFullYear());

    fetch(`/yearly_event_data/${currentYear}`)
    .then(response => response.json())
    .then(data => {
        console.log("Received data: ", data);

        document.querySelector('#daily-average').textContent = Number(data.daily_average).toFixed(2);
        document.querySelector('#weekly-average').textContent = Number(data.weekly_average).toFixed(2);
        document.querySelector('#monthly-average').textContent = Number(data.monthly_average).toFixed(2);

        var ctx = document.getElementById('weeklyEventsChart').getContext('2d');

        if (myWeeklyChart) {
            myWeeklyChart.destroy();
        }

        let weeklyEventCounts = data.weekly_event_data.map(weekData => weekData[0]);
        let maxEventValue = Math.max(...weeklyEventCounts);
        let maxEventIndex = weeklyEventCounts.indexOf(maxEventValue);

        document.querySelector('#busiest-week').textContent = `Busiest Week: ${maxEventIndex+1} : Events: ${maxEventValue}`;

        let pointBackgroundColors = weeklyEventCounts.map((value, index) =>
            index === maxEventIndex ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 123, 255, 0.5)'
        );

        myWeeklyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: weeklyEventCounts.map((value, index) => `Week ${index+1}`),
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
    });
}

// Global variable to hold the Chart.js instance for the monthly chart.
var myMonthlyChart = null;

function eventUpdateMonth() {
    console.log("currentYear: ", currentYear);
    console.log("accountCreationYear: ", accountCreationYear);
    var monthlyTabActive = document.getElementById('monthly-tab').classList.contains('active');
    if (!monthlyTabActive) {
        return;
    }

    yearTitle.textContent = currentYear;
    console.log("Fetching data for month: ", currentYear);

    chevronLeft.classList.toggle("disabled", currentYear <= accountCreationYear);
    chevronRight.classList.toggle("disabled", currentYear >= new Date().getFullYear());

    fetch(`/yearly_event_data/${currentYear}`)
    .then(response => response.json())
    .then(data => {
        console.log("Received data: ", data);

        document.querySelector('#daily-average').textContent = Number(data.daily_average).toFixed(2);
        document.querySelector('#weekly-average').textContent = Number(data.weekly_average).toFixed(2);
        document.querySelector('#monthly-average').textContent = Number(data.monthly_average).toFixed(2);

        var ctx = document.getElementById('monthlyEventsChart').getContext('2d');

        if (window.myMonthlyChart) {
            window.myMonthlyChart.destroy();
        }

        let maxEventValue = Math.max(...data.monthly_event_data);
        let maxEventIndex = data.monthly_event_data.indexOf(maxEventValue);

        var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"];
        var monthString = monthNames[maxEventIndex];

        document.querySelector('#busiest-month').textContent = `Busiest Month: ${monthString} : Events: ${maxEventValue}`;

        let dataZero = [];
        let dataNonZero = [];

        data.monthly_event_data.forEach((val, idx) => {
            if (val === 0) dataZero.push(idx+1);
            else dataNonZero.push(idx+1);
        });

        let dataNonZeroValues = dataNonZero.map(idx => data.monthly_event_data[idx-1]);

        let pointBackgroundColors = new Array(12).fill('rgba(0, 123, 255, 0.5)');
        pointBackgroundColors[maxEventIndex] = 'rgba(255, 0, 0, 0.5)';

        window.myMonthlyChart = new Chart(ctx, {
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
            if (document.getElementById('daily-tab').classList.contains('active')) {
                eventUpdateYear();
            } else if (document.getElementById('weekly-tab').classList.contains('active')) {
                eventUpdateWeek();
            } else if (document.getElementById('monthly-tab').classList.contains('active')) {
                eventUpdateMonth();
            }
        }
    });

    chevronRight.addEventListener("click", function() {
        if (currentYear < new Date().getFullYear()) {
            currentYear++;
            if (document.getElementById('daily-tab').classList.contains('active')) {
                eventUpdateYear();
            } else if (document.getElementById('weekly-tab').classList.contains('active')) {
                eventUpdateWeek();
            } else if (document.getElementById('monthly-tab').classList.contains('active')) {
                eventUpdateMonth();
            }
        }
    });

    document.getElementById('daily-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(eventUpdateYear, 1000);
    });

    document.getElementById('weekly-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(eventUpdateWeek, 1000);
    });

    document.getElementById('monthly-tab').addEventListener('shown.bs.tab', function() {
        setTimeout(eventUpdateMonth, 1000);
    });
    
    eventUpdateYear();
    eventUpdateWeek();
    eventUpdateMonth();
}

// Task Insight js

var dailyTasksChart = null;
var weeklyTasksChart = null;
var monthlyTasksChart = null;

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

            const dailyLabels = dailyTaskData.map(entry => entry.date);
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
                                        
                                        const monthNames = ["January", "February", "March", "April", "May", "June",
                                                            "July", "August", "September", "October", "November", "December"];
                                        switch (chartType) {
                                            case 'daily': {
                                                const dateObj = parseLocalDate(dateStr);
                                                const month = monthNames[dateObj.getMonth()];
                                                const day = dateObj.getDate();
                                                return `${month} ${day}`;
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
        if (document.getElementById('daily-tab').classList.contains('active')) {
            updateTaskCharts(currentYearTasks, 'daily');
        } else if (document.getElementById('weekly-tab').classList.contains('active')) {
            updateTaskCharts(currentYearTasks, 'weekly');
        } else if (document.getElementById('monthly-tab').classList.contains('active')) {
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

    document.getElementById('daily-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    document.getElementById('weekly-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    document.getElementById('monthly-tab').addEventListener('shown.bs.tab', () => {
        setTimeout(updateChart, 1000);
    });

    updateChart();
}