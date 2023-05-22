function updateTaskStatus(checkboxElem, taskId) {
  const isChecked = checkboxElem.checked;
  let taskMessage;

  if (document.getElementById("taskCompleteMessage" + taskId)) {
    taskMessage = document.getElementById("taskCompleteMessage" + taskId);
  } else if (document.getElementById('task-done-message')) {
    taskMessage = document.getElementById('task-done-message');
  }
  
  
  fetch(`/tasks/${taskId}/`, {
      method: 'POST',
      headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest'
      },
      body: 'status=' + encodeURIComponent(isChecked)
  })
  .then(response => {
      console.log("Response status: ", response.status);
      console.log("Response headers: ", response.headers);
      return response.json()
  })
  .then(data => {
    console.log("Response data: ", data);
      if (data.success) {
          console.log('Task status updated successfully');
      if (isChecked) {
        if (taskMessage.id === "task-done-message") {
          taskMessage.style.display = 'block';
        } else {
          taskMessage.style.display = 'inline';
        }
        // Set a timeout to hide the message after 5 seconds
        setTimeout(function() {
          taskMessage.classList.add('fadeOut');
          // Wait for the animation to finish and then hide the element
          setTimeout(function() {
              taskMessage.style.display = 'none';
              taskMessage.classList.remove('fadeOut');
          }, 2000);
        }, 2000);
      
      } else {
        taskMessage.style.display = 'none';
      }
      } else {
          console.error('Failed to update task status:', data.message);
      }
  })
  .catch(error => {
      console.error('Failed to update task status', error);
  });
}