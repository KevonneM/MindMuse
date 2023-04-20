var intervalRunning = false;

function update_current_time() {
  if (!intervalRunning) {
    var day_of_week_element = document.getElementById('day_of_week');
    var date_element = document.getElementById('date');
    var current_time_element = document.getElementById('current_time');

    var now = new Date();
    var current_time = new Date().toLocaleTimeString();

    var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    var day_of_week = days[now.getDay()];
    
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var date_string = `${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;

    day_of_week_element.textContent = day_of_week;
    date_element.textContent = date_string;
    current_time_element.textContent = current_time;

    intervalRunning = true;
    
    // Update time every second.
    setInterval(function() {
      current_time = new Date().toLocaleTimeString();
      current_time_element.textContent = current_time;

    }, 1000);

    // Update day of week and date every minute.
    setInterval(function() {
      now = new Date();

      day_of_week = days[now.getDay()];
      day_of_week_element.textContent = day_of_week;
      date_string = `${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;
      date_element.textContent = date_string;
    }, 60000);
  }
}

function detectTimezoneAndSet() {
  var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  fetch('/set_timezone', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: 'timezone=' + encodeURIComponent(timezone)
  })
  .then(response => {
    if (response.ok) {
      window.location.reload();
    } else {
      console.error('Failed to set timezone');
    }
  })
  .catch(error => {
    console.error('Failed to set timezone', error);
  });
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function updateWeatherData(cityName) {
  console.log('Updating weather...');
  const weatherIconUrl = (iconCode) => `http://openweathermap.org/img/wn/${iconCode}.png`;
  const cityParam = cityName ? cityName : '';
  fetch(`/fetch_weather/${cityParam}`)
      .then(response => response.json())
      .then(data => {
          document.getElementById('city_name').innerText = data.city_name;
          document.getElementById('temperature').innerText = data.temperature + '°F';
          document.getElementById('feels_like').textContent = `Feels like: ${data.feels_like}°F, `;
          document.getElementById('condition').innerText = data.condition;
          document.querySelector('.humidity-value').textContent = data.humidity;
          document.querySelector('.wind-speed-value').textContent = data.wind_speed;
          
          const weatherIcon = document.getElementById('weather-icon');
          weatherIcon.src = weatherIconUrl(data.icon);
          weatherIcon.alt = data.condition;

          // Schedule the next update in 5 minutes (300,000 ms).
          setTimeout(updateWeatherData, 500000);
      })
      .catch(error => {
          console.error('Error fetching weather data:', error);
      });
}

// Function to handle city input
function fetchWeatherByCity() {
  const cityName = document.getElementById('cityInput').value;
  if (cityName) {
    updateWeatherData(cityName);
  } else {
    alert('Please enter a city name.');
  }
}

function fetchCityByIP() {
  fetch('http://ip-api.com/json/')
    .then(response => response.json())
    .then(data => {
      const cityName = data.city;
      if (cityName) {
        updateWeatherData(cityName);
      } else {
        console.error('Failed to fetch city by IP:', data);
      }
    })
    .catch(error => {
      console.error('Error fetching city by IP:', error);
    });
}

function getLastTrackedCity() {
  fetch('/get_last_tracked_city/')
    .then(response => response.json())
    .then(data => {
      const lastTrackedCity = data.last_tracked_city;
      if (lastTrackedCity) {
        updateWeatherData(lastTrackedCity);
      } else {
        fetchCityByIP();
      }
    })
    .catch(error => {
      console.error('Error fetching last tracked city:', error);
    });
}