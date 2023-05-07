// toggles completion count from task form
function toggleTaskFormCompletionCount() {
    const completionCountInput = document.querySelector('#id_completion_count');
    const formElement = document.querySelector('form[data-instance-pk]');
    const instancePk = formElement ? formElement.getAttribute('data-instance-pk') : null;
    
    if (completionCountInput && instancePk !== null) {
      function toggleCompletionCount() {
        if (!completionCountInput.value && !Boolean(parseInt(instancePk))) {
          completionCountInput.parentElement.parentElement.style.display = 'none';
        } else {
          completionCountInput.parentElement.parentElement.style.display = '';
        }
      }
      
      toggleCompletionCount();
    }
  }
  
// adds checkboxes and updates task status with checkboxes using ajax
function updateCompletionCount(checkboxElem, taskId, completionGoal) {
    const isChecked = checkboxElem.checked;
    const taskDoneMessage = document.getElementById("task-done-message");

    const checkboxes = document.querySelectorAll(`input[type="checkbox"]`);
    let checkedCount = 0;

    checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
        checkedCount++;
        }
    });

    fetch(`/tasks/${taskId}/`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
        },
        body: 'completion_count=' + encodeURIComponent(checkedCount)
    })
    .then(response => {
        console.log("Response status: ", response.status);
        console.log("Response headers: ", response.headers);
        return response.json();
    })
    .then(data => {
        console.log("Response data: ", data);
        if (data.success) {
        console.log('Completion count updated successfully');
        if (checkedCount >= completionGoal) {
            taskDoneMessage.style.display = "block";
        } else {
            taskDoneMessage.style.display = "none";
        }
        } else {
        console.error('Failed to update completion count:', data.message);
        }
    })
    .catch(error => {
        console.error('Failed to update completion count', error);
    });
}

document.addEventListener('DOMContentLoaded', toggleTaskFormCompletionCount);