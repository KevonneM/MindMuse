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

    if(day_of_week_element) day_of_week_element.textContent = day_of_week;
    if(date_element) date_element.textContent = date_string;
    if(current_time_element) current_time_element.textContent = current_time;

    intervalRunning = true;
    
    // Update time every second.
    setInterval(function() {
      current_time = new Date().toLocaleTimeString();
      if(current_time_element) current_time_element.textContent = current_time;

    }, 1000);

    // Update day of week and date every minute.
    setInterval(function() {
      now = new Date();

      day_of_week = days[now.getDay()];
      if(day_of_week_element) day_of_week_element.textContent = day_of_week;
      date_string = `${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;
      if(date_element) date_element.textContent = date_string;
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
      console.log("Detected user's timezone: ", timezone)
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
      const cityNameElement = document.getElementById('city_name');
      const temperatureElement = document.getElementById('temperature');
      const feelsLikeElement = document.getElementById('feels_like');
      const conditionElement = document.getElementById('condition');
      const humidityElement = document.querySelector('.humidity-value');
      const windSpeedElement = document.querySelector('.wind-speed-value');
      const weatherIconElement = document.getElementById('weather-icon');

      if(cityNameElement) cityNameElement.innerText = data.city_name;
      if(temperatureElement) temperatureElement.innerText = data.temperature + '°F';
      if(feelsLikeElement) feelsLikeElement.textContent = `Feels like: ${data.feels_like}°F, `;
      if(conditionElement) conditionElement.innerText = data.condition;
      if(humidityElement) humidityElement.textContent = data.humidity;
      if(windSpeedElement) windSpeedElement.textContent = data.wind_speed;
      if(weatherIconElement) {
        weatherIconElement.src = weatherIconUrl(data.icon);
        weatherIconElement.alt = data.condition;
      }

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

// set up event listeners upon DOMContentLoaded event completion.

function init() {
  update_current_time();
  var refreshButton = document.getElementById('refreshButton');
  var submitCity = document.getElementById('submitCity');
  var useIP = document.getElementById('useIP');

  if (refreshButton) refreshButton.addEventListener('click', getLastTrackedCity);
  if (submitCity) submitCity.addEventListener('click', fetchWeatherByCity);
  if (useIP) useIP.addEventListener('click', fetchCityByIP);
  
  if (document.getElementById('city_name')) {
    getLastTrackedCity();
  }
}

document.addEventListener('DOMContentLoaded', init);

// incoming weekly events js

function updateEventStatus() {
  
  let endpoint = '/get_event_status/';

  fetch(endpoint)
  .then(response => response.json())
  .then(data => {
      if (data.has_visible_events) {
          document.querySelector('.no-events-message').style.display = 'none';
      } else {
          document.querySelector('.no-events-message').style.display = 'block';
      }
  })
  .catch(error => {
      console.error('There was an error fetching event status:', error);
  });
}

function updateCountdowns() {
  const countdowns = document.querySelectorAll('.countdown');
  const now = new Date();

  countdowns.forEach(countdown => {
    const eventStartTime = new Date(parseInt(countdown.dataset.eventStartTime) * 1000);
    const eventEndTime = new Date(parseInt(countdown.dataset.eventEndTime) * 1000);
    const fiveMinutesInMilliseconds = 5 * 60 * 1000;
    const remainingTime = eventStartTime - now;
    const endTimePassed = now - eventEndTime;

    // If the event hasn't started yet, countdown to start time
    if (remainingTime > 0) {
      countdown.textContent = 'Starts in: ' + formatCountdown(remainingTime);
    }
    // If the event has started but not ended, countdown to end time
    else if (now < eventEndTime) {
      const remainingEndTime = eventEndTime - now;
      countdown.textContent = 'Ends in: ' + formatCountdown(remainingEndTime);
    }
    // If the event has ended less than five minutes ago, countdown until removal
    else if (endTimePassed < fiveMinutesInMilliseconds) {
      countdown.textContent = 'Removing in: ' + formatCountdown(fiveMinutesInMilliseconds - endTimePassed);
    }
    // If the event has ended more than five minutes ago, remove it
    else {
      countdown.parentElement.remove();
    }
  });
}

// This function formats the countdown time (given in milliseconds)
function formatCountdown(time) {
  const days = Math.floor(time / (1000 * 60 * 60 * 24));
  const hours = Math.floor((time % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((time % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((time % (1000 * 60)) / 1000);

  let countdownText = '';

  if (days > 0) {
    countdownText += `${days}d `;
  }
  if (hours > 0) {
    countdownText += `${hours}h `;
  }
  if (minutes > 0) {
    countdownText += `${minutes}m `;
  }
  if (seconds > 0) {
    countdownText += `${seconds}s`;
  }

  return countdownText.trim();
}

setInterval(updateCountdowns, 1000);