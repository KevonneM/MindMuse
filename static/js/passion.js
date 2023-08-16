function recordPassionActivity(checkboxElem, passionId, dateStr, accountCreationYear) {
    const isChecked = checkboxElem.checked;

    const date = new Date(dateStr);
    const currentDate = new Date();

    currentDate.setHours(0, 0, 0, 0);

    if (date.getFullYear() < accountCreationYear) {
        alert('You cannot record activity for years before your account was created.');
        checkboxElem.checked = false;
        return;
    } else if (date > currentDate) {
        alert('You cannot record activity for future dates.');
        checkboxElem.checked = false;
        return;
    }

    // Only record activity if the checkbox is checked
    if (isChecked) {
        let hours = prompt("Enter the duration of your activity in hours (0-24)");

        if (hours === null) {
            checkboxElem.checked = false;
            return;
        }

        // Validation
        while (!/^[0-9]{1,2}$/.test(hours) || parseInt(hours) < 0 || parseInt(hours) > 24) {
            alert('Invalid hour input. Please enter a value between 0-24');
            hours = prompt("Enter the duration of your activity in hours (0-24)");
        }

        let minutes = prompt("Enter the duration of your activity in minutes (0-59, in increments of 5)");

        if (minutes === null) {
            checkboxElem.checked = false;
            return;
        }

        while (!/^[0-9]{1,2}$/.test(minutes) || parseInt(minutes) % 5 !== 0 || parseInt(minutes) < 0 || parseInt(minutes) > 59) {
            alert('Invalid minute input. Please enter a value between 0-59 in increments of 5');
            minutes = prompt("Enter the duration of your activity in minutes (0-59, in increments of 5)");
        }

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
        } else {
            checkboxElem.checked = true;
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
            console.log(response);
            let activitiesExist = response.activities_exist;

            // Update the checkboxes
            for (let i = 0; i < activitiesExist.length; i++) {
                let checkbox = document.getElementById('checkbox' + i + passionId);
                checkbox.checked = activitiesExist[i];
            }
        } else {
            console.error('AJAX request failed with status ' + xhr.status);
        }
    }

    xhr.send();
}