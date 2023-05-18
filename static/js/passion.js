function recordPassionActivity(checkboxElem, passionId, dateStr) {
    const isChecked = checkboxElem.checked;

    // Only record activity if the checkbox is checked
    if (isChecked) {
        let duration = prompt("Enter the duration of your activity in the format HH:MM");

        // Validation
        while (!/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/.test(duration)) {
            alert('Invalid duration. Please use format HH:MM');
            duration = prompt("Enter the duration of your activity in the format HH:MM");
        }

        // Extract hours and minutes
        const [hours, minutes] = duration.split(':');

        // Convert the date string to a Date object
        const date = new Date(dateStr);

        // Send an AJAX request to the server to record the activity
        fetch(`/passions/record_activity/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                'passion_id': passionId,
                'date': date.toISOString().split('T')[0], // Format date as "YYYY-MM-DD"
                'hours': hours,
                'minutes': minutes
            })
        })
        .then(response => {
            console.log(response)
            console.log("Response status: ", response.status);
            console.log("Response headers: ", response.headers);
            return response.json();
        })
        .then(data => {
            console.log("Response data: ", data);
            if (data.success) {
                console.log('Passion activity recorded successfully');
            } else {
                console.error('Failed to record passion activity:', data.message);
            }
        })
        .catch(error => {
            console.error('Failed to record passion activity', error);
        });
    } else {
        // Prompt the user to confirm the deletion
        const confirmDelete = confirm("Do you want to remove the recorded activity?");
        if (confirmDelete) {
            // Send an AJAX request to the server to delete the activity
            fetch(`/passions/delete_activity/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    'passion_id': passionId,
                    'date': dateStr,
                })
            })
            .then(response => {
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Passion activity deleted successfully');
                } else {
                    console.error('Failed to delete passion activity:', data.message);
                }
            })
            .catch(error => {
                console.error('Failed to delete passion activity', error);
            });
        }
    }
}

function updatePassionProgress(passionId) {
    console.log('Checking for current passion activity week.')
    
    let xhr = new XMLHttpRequest();

    xhr.open('GET', '/passions/update_passion_progress/' + passionId + '/', true);


    xhr.onload = function() {
        if (xhr.status == 200) {
            // Parse the JSON response
            let response = JSON.parse(xhr.responseText);
            let activitiesExist = response.activities_exist;

            // Update the checkboxes
            for (let i = 0; i < activitiesExist.length; i++) {
                let checkbox = document.getElementById('checkbox' + i);
                checkbox.checked = activitiesExist[i];
            }
        } else {
            console.error('AJAX request failed with status ' + xhr.status);
        }
    }

    xhr.send();
}