function openColorPicker(id) {
    var picker = document.getElementById(id).jscolor;
    picker.show();
}

window.onload = function() {
    currentUserColors();
    document.getElementById('offcanvasScrolling').addEventListener('shown.bs.offcanvas', function () {
        const colorInputs = document.querySelectorAll('.jscolor');

        colorInputs.forEach(input => {
            input.addEventListener('input', () => {
                const field = input.id.replace('-input', '');
                const hexColor = input.value;
                updateColor(field, hexColor);
                applyColor(field, '#' + hexColor);
            });
        });
    });
    document.querySelector('.color-layout-reset').addEventListener('click', resetColors);

    document.querySelectorAll('#myTab .nav-link').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            currentUserColors().then(colorData => {
                if (colorData && colorData['tab-color']) {
                    document.querySelectorAll('#myTab .nav-link').forEach(inactiveTab => {
                        inactiveTab.style.backgroundColor = ''; 
                    });
                    event.target.style.backgroundColor = colorData['tab-color'];
                }
            });
        });
    });
};

/* Js to update color field in the offcanvas */
function updateColor(field, value) {
    let paintbrushIconId = field + '-input-paintbrush-icon';
    
    var paintbrushIcon = document.getElementById(paintbrushIconId);

    if (paintbrushIcon) {
        var pathElement = paintbrushIcon.querySelector('path');
        if (pathElement) {
            pathElement.setAttribute('fill', value);
        } else {
            console.error('No path element found in the SVG icon for field:', field);
        }
    } else {
        console.error('No paintbrush icon found for field:', field);
    }
    
    fetch('/users/update_color/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({[field]: value}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Color updated successfully');
            applyColor(field, value);
        } else {
            console.error('Error updating color:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/* Js to apply color to page elements */
function applyColor(field, value) {
    
    switch(field) {
        case 'background-color':
            let backgroundColorElements = [
                'custom-color-background',
                'custom-color-background-html',
                'custom-color-background-home-html'
            ];
            backgroundColorElements.forEach(elementId => {
                let element = document.getElementById(elementId);
                console.log('Element:', elementId, 'Value:', value);
                if(element) element.style.setProperty('background-color', value, 'important');
            });
            break;
        case 'navbar-color':
            let navbarColorElements = ['custom-color-nav'];
            navbarColorElements.forEach(elementId => {
                let element = document.getElementById(elementId);
                if(element) element.style.setProperty('background-color', value, 'important');
            });
            /* background color for icon 3 of nav */
            /*document.getElementById('custom-color-navicon-3-back').setAttribute('fill', value);*/
            break;
        case 'button-color':
            document.documentElement.style.setProperty('--btn-primary-bg', value);
            document.documentElement.style.setProperty('--btn-primary-border', value);
            break;            
        case 'tab-color':
            document.documentElement.style.setProperty('--tab-active-bg', value);
            let tabColorElementsMain = [
                '.nav-link-hub.active',
                '.nav-link-insights.active',
                '.nav-link-options.active',

                '#daily-tab.active',
                '#weekly-tab.active',
                '#monthly-tab.active',

                '#quoteOfDay-tab.active',
                '#savedQuotes-tab.active',
            ];
            tabColorElementsMain.forEach(selector =>{
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('background-color', value, 'important');
            });
            
            let dailyWeeklyMonthlyTabs = ['#daily-tab', '#weekly-tab', '#monthly-tab'];
            let quoteTabs = ['#quoteOfDay-tab', '#savedQuotes-tab'];

            // Reset color for inactive tabs
            function updateTabColors(tabGroup, activeTab, color) {
                tabGroup.forEach(selector => {
                    document.querySelectorAll(selector).forEach(tab => {
                        if (tab === activeTab) {
                            tab.style.setProperty('background-color', color, 'important');
                        } else {
                            tab.style.backgroundColor = '';
                        }
                    });
                });
            }

            dailyWeeklyMonthlyTabs.forEach(selector => {
                document.querySelectorAll(selector).forEach(tab => {
                    tab.addEventListener('click', function() {
                        updateTabColors(dailyWeeklyMonthlyTabs, this, value);
                    });
                });
            });

            quoteTabs.forEach(selector => {
                document.querySelectorAll(selector).forEach(tab => {
                    tab.addEventListener('click', function() {
                        updateTabColors(quoteTabs, this, value);
                    });
                });
            });
            
            let tabColorElementsInsights = [

            ];
            tabColorElementsInsights.forEach(selector =>{
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('background-color', value, 'important');
            });
            break;
        case 'logo-greeting-color':
            let logoElements = [
                'custom-color-logo-pt1', 'custom-color-logo-pt2', 'custom-color-logo-pt3', 
                'custom-color-logo-pt4', 'custom-color-logo-pt5', 'custom-color-logo-pt6', 
                'custom-color-logo-pt7', 'custom-color-logo-pt8', 'custom-color-logo-pt9', 
                'custom-color-logo-pt10', 'custom-color-logo-pt11', 'custom-color-logo-pt12', 
                'custom-color-logo-pt13', 'custom-color-logo-pt14', 'custom-color-logo-pt15', 
                'custom-color-logo-pt16', 'custom-color-logo-pt17', 'custom-color-logo-pt18', 
                'custom-color-logo-pt19', 'custom-color-logo-pt20', 'custom-color-logo-pt21', 
                'custom-color-logo-pt22', 'custom-color-logo-pt23', 'custom-color-logo-pt24', 
                'custom-color-logo-pt25', 'custom-color-navicon-1', 'custom-color-navicon-2', 
                'custom-color-navicon-2-pt2', 'custom-color-navicon-3'
            ];
            logoElements.forEach(elementId => {
                let element = document.getElementById(elementId);
                if(element) element.setAttribute('fill', value);
            });
        
            let greetingElement = document.getElementById('custom-color-greeting');
            if(greetingElement) greetingElement.style.color = value;
            break;
        case 'card-header-color':
            /* Main Hub headers */
            let mainHeaders = [
                'custom-color-incoming-events-header',
                'custom-color-schedule-header',
                'custom-color-tasks-header',
                'custom-color-passions-header',
                'custom-color-weather-header',
                'custom-color-weather-footer',
                'custom-color-quotes-header',
            ];
            mainHeaders.forEach(headerId => {
                let element = document.getElementById(headerId);
                if(element) element.style.setProperty('background-color', value, 'important');
            });

            /* Insight headers */
            let insightHeaders = [
                'custom-color-overview-header',
                'custom-color-passion-insight-header',
                'custom-color-task-insight-header',
                'custom-color-event-insight-header'
            ];
            
            insightHeaders.forEach(headerId => {
                let element = document.getElementById(headerId);
                if(element) element.style.setProperty('background-color', value, 'important');
            });            
            break;
        case 'card-interior-color':
            let cardInteriors = [
                '#custom-color-incoming-events-interior',
                '#custom-color-schedule-interior',
                '#custom-color-schedule-interiorpt2',
                '#myTabContent',
                '.dailyTaskListPills',
                '#dailyTaskList',
                '#passionContent',
                '#custom-color-weather-interior',
                '#quoteTabsContent',
                '.qotd-icon-container',
            ];

            cardInteriors.forEach(selector => {
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('background-color', value, 'important');
            });

            let insightInteriors = [
                '#custom-color-overview-interior',
            ]

            insightInteriors.forEach(selector => {
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('background-color', value, 'important');
            }); 
            break;
        case 'card-header-text-color':
            let cardHeaderText = [
                '.custom-color-incoming-events-header-text',
                '.custom-color-schedule-header-text',
                '#custom-color-tasks-header-text',
                '#custom-color-passions-header-text',
                '.custom-color-weather-header-text',
            ];

            cardHeaderText.forEach(selector => {
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('color', value, 'important');
            });

            /* Insight header text */
            let insightHeaderText = [
                '#custom-color-overview-header-text',
                '#custom-color-passion-header-text',
                '#custom-color-task-header-text',
                '#custom-color-event-header-text',
                '#custom-color-passion-header-year-text',
                '#custom-color-task-header-year-text',
                '#custom-color-event-header-year-text',
            ];

            insightHeaderText.forEach(selector => {
                let element = document.querySelector(selector);
                if(element) element.style.setProperty('color', value, 'important');
            }); 
            break;
        case 'small-text-color':
            let hubSmallText = [
                '#incomingSmallText',
                '#dailyTaskSmallText',
                '#weeklyTaskSmallText',
                '#monthlyTaskSmallText',
                '.passion-details',
            ]

            hubSmallText.forEach(selector => {
                document.querySelectorAll(selector).forEach(element => {
                    element.style.setProperty('color', value, 'important');
                });
            });
            break;
        case 'dropdown-color':
            document.documentElement.style.setProperty('--dropdown-bg-color', value);
            document.querySelectorAll('.dropdown-menu').forEach(element => {
                element.style.setProperty('background-color', value, 'important');
            });
            break;
        case 'button-text-color':
            document.querySelectorAll('.btn-primary').forEach(button => {
                button.style.setProperty('color', value, 'important');

                let svgElements = button.querySelectorAll('svg *');
                svgElements.forEach(svgchild => {   
                    svgchild.style.fill = value;
                });
            });
            break;
        case 'tab-text-color':
            let tabTextColorElements = [
                '.nav-link-hub',
                '#nav-hub-text',
                '.nav-link-insights',
                '#nav-ins-text',
                '.nav-link-options',
                '#daily-tab',
                '#weekly-tab',
                '#monthly-tab',
                '#quoteOfDay-tab',
                '#savedQuotes-tab',
            ];
        
            tabTextColorElements.forEach(selector => {
                document.querySelectorAll(selector).forEach(tab => {
                    tab.style.setProperty('color', value, 'important');
                });
            });
            break;
        case 'dropdown-text-color':
            let dropdownTextElements = [
                '.dropdown-item',
            ];
        
            dropdownTextElements.forEach(selector => {
                document.querySelectorAll(selector).forEach(element => {
                    element.style.setProperty('color', value, 'important');
        
                    let svgElements = element.querySelectorAll('svg *');
                    svgElements.forEach(svgChild => {
                        if (svgChild.getAttribute('stroke')) {
                            // If the SVG child element has a stroke attribute, change only the stroke color
                            svgChild.style.stroke = value;
                        } else if (svgChild.getAttribute('fill') && svgChild.getAttribute('fill') !== 'none') {
                            // If the SVG child element has a fill attribute (and is not 'none'), change only the fill color
                            svgChild.style.fill = value;
                        }
                    });
                });
            });
            break;                        
        default:
            console.error('Unknown color field:', field);
    }
}

/* Js to reset to default page color values */
function resetColors() {
    fetch('/users/reset_color/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Color reset successfully');
            currentUserColors();
        } else {
            console.error('Error resetting color:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/* Js to Retrieve current color selection from db */
async function currentUserColors() {
    try {
        let response = await fetch('/users/get_color_selection/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });
        let colorData = await response.json();
        console.log(colorData);
        for (let field in colorData) {
            let value = colorData[field];
            console.log("field:", field, 'value:', value)
            applyColor(field, value);
            updateColor(field, value);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}