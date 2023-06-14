var starredQuoteIndex = -1;
var quoteIndex = 0;
var quotes = [];
var timer = null;
var inactivityTimer = null;

async function getQuotes() {
    let response = await fetch('/quotes/get_starred/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
    });

    let data = await response.json();

    quotes = data.quotes;
    starredQuoteIndex = quotes.findIndex(quote => quote.starred);

    console.log(data.status, quotes)

    if (data.status === "quote found") {
        displayQuote(starredQuoteIndex, true);
    } else if (data.status === "no starred quote") {
        quoteIndex = 0;
        displayQuote(quoteIndex, false);
        startCarousel();
    } else {
        console.error("Error while fetching quotes: ", data.status);
    }
}

function displayQuote(index, shouldPause) {
    let quote = quotes[index];

    let newCarouselItem = document.createElement('div');
    newCarouselItem.className = 'carousel-item';
    newCarouselItem.style.opacity = 0;
    newCarouselItem.innerHTML = `
        <div class="quote-card">
            <p class="quote">"${quote.quote}" - ${quote.author}</p>
            <div class="star-container">
                <i class="quote-star fas fa-star" data-quote-id="${quote.id}"></i>
            </div>
        </div>`;

    let carouselInner = document.getElementById('carousel-inner');

    carouselInner.appendChild(newCarouselItem);

    // If there are any other quotes in the carousel, fade them out
    let oldCarouselItems = Array.from(carouselInner.getElementsByClassName('carousel-item')).filter(item => item !== newCarouselItem);
    if (oldCarouselItems.length > 0) {
        oldCarouselItems.forEach(item => {
            item.style.opacity = 0;
            setTimeout(() => {
                // error handling for removal of child node
                if (carouselInner.contains(item)) {
                    carouselInner.removeChild(item);
                } else {
                    console.warn("Attempted to remove an element that is not a child of the carouselInner");
                }
            }, 1000);
        });
    }

    // Delay the fade-in of the new item until after the old item has started fading out
    setTimeout(() => {
        newCarouselItem.style.opacity = 1;
        newCarouselItem.classList.add('active');  // Add the 'active' class

        newCarouselItem.querySelector(".quote-star").addEventListener("click", function(e) {
            handleStarClick(e.target);
        });

        if (shouldPause || (starredQuoteIndex !== -1 && index === starredQuoteIndex)) {
            pauseCarousel();
        } else if (starredQuoteIndex !== -1 && quoteIndex !== starredQuoteIndex) {
            startInactivityTimer();
        } else {
            startCarousel();
        }
        
    // Adjust delay based on existance.
    }, oldCarouselItems.length > 0 ? 700 : 0); 
}

function startCarousel() {
    // Cancel the previous timer if exists
    if (timer) {
        clearInterval(timer);
    }

    timer = setInterval(function () {
        quoteIndex = (quoteIndex + 1) % quotes.length;
        displayQuote(quoteIndex, false);
    }, 10000);
}

function pauseCarousel() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

function handleStarClick(starIcon) {
    fetch('/quotes/' + starIcon.getAttribute('data-quote-id') + '/star/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            getQuotes();
        } else {
            console.error("Error while handling star click:", data.status);
        }
    })
    .catch(error => console.error('Error:', error));
}

function startInactivityTimer() {
    // Cancel the previous timer
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }

    // If there is a starred quote, set a new timer to navigate to it after 20 seconds
    if (starredQuoteIndex !== -1 && quoteIndex !== starredQuoteIndex) {
        inactivityTimer = setTimeout(function () {
            displayQuote(starredQuoteIndex, true);
            pauseCarousel();
        }, 20000);
    }
}

window.onload = function () {
    getQuotes();
    
    document.querySelector('#savedQuotesCarousel .carousel-control-prev').addEventListener('click', function (e) {
        e.preventDefault();
        prevQuote();
    });
    document.querySelector('#savedQuotesCarousel .carousel-control-next').addEventListener('click', function (e) {
        e.preventDefault();
        nextQuote();
    });
};

function nextQuote() {
    quoteIndex = (quoteIndex + 1) % quotes.length;
    displayQuote(quoteIndex, false);
}

function prevQuote() {
    quoteIndex = (quoteIndex - 1 + quotes.length) % quotes.length;
    displayQuote(quoteIndex, false);
}