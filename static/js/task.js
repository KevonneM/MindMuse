function updateTaskStatus(checkboxElem, taskId, isModalCheckbox) {
  const isChecked = checkboxElem.checked;
  const taskTitleElement = document.querySelector(`#taskCheckbox${taskId}`).nextElementSibling.nextElementSibling;
  
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
        applyStrikethroughOnInit();

    if (isChecked) {
      checkboxElem.checked = true;
      taskTitleElement.classList.add('strikethrough');
      taskTitleElement.classList.add('animate-strikethrough');
      
    } else {
      checkboxElem.checked = false;
      taskTitleElement.classList.remove('strikethrough');
      taskTitleElement.classList.remove('animate-strikethrough');
    }
    syncCheckboxStatus(checkboxElem, taskId, isModalCheckbox);
    } else {
        console.error('Failed to update task status:', data.message);
    }
  })
  .catch(error => {
      console.error('Failed to update task status', error);
  });
}

function syncCheckboxStatus(checkboxElem, taskId, isModalCheckbox) {
  // Get checkbox id based on where the checkbox is clicked, either modal or hub
  let checkboxId = isModalCheckbox ? `taskCheckbox${taskId}` : `modalTaskCheckbox${taskId}`;
  
  // get the other checkbox element
  let otherCheckbox = document.getElementById(checkboxId);

  // update its status to match
  if (otherCheckbox) {
      otherCheckbox.checked = checkboxElem.checked;
  }
}

function applyStrikethroughOnInit() {
  const taskPanes = ['#daily', '#weekly', '#monthly'];

  taskPanes.forEach(pane => {
    const taskPaneElem = document.querySelector(pane);
    if (taskPaneElem) {
      const checkboxes = taskPaneElem.querySelectorAll('.task-checkbox');
      checkboxes.forEach(checkbox => {
        const isChecked = checkbox.checked;
        const taskTitleElement = checkbox.nextElementSibling.nextElementSibling;
        if (isChecked) {
          taskTitleElement.classList.add('strikethrough');
          taskTitleElement.classList.add('animate-strikethrough');
        } else {
          taskTitleElement.classList.remove('strikethrough');
          taskTitleElement.classList.remove('animate-strikethrough');
        }
      });
    }
  });
}

document.addEventListener('show.bs.tab', function (event) {
  if (['daily-tab', 'weekly-tab', 'monthly-tab'].includes(event.target.id)) {
    setTimeout(() => {
      applyStrikethroughOnInit();
    }, 0);
  }
});

window.addEventListener('load', applyStrikethroughOnInit);