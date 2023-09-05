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

    if (!quote) {
        console.error("No saved quotes for current user");
        return;
    }

    let noQuotesMessage = document.getElementById('noQuotesMessage');
    if (noQuotesMessage) {
        noQuotesMessage.remove();
    }

    let starClass = quote.starred ? ' starred': '';

    let newCarouselItem = document.createElement('div');
    newCarouselItem.className = 'carousel-item';
    newCarouselItem.style.opacity = 0;
    newCarouselItem.innerHTML = `
        <div class="quote-card">
            <div class="quote-content-wrapper">
                <div class="quote-content">
                    <p class="quote">"${quote.quote}" - ${quote.author}</p>
                </div>
            </div>
            <div class="action-container">
                <button class="quote-edit" data-quote-id="${quote.id}" data-bs-toggle="tooltip" title="Edit quote" style="background: none; border: none;">
                    <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="margin-right: 5px;">
                    <g fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                        <path d="M7 7H6a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2v-1"></path>
                        <path d="M20.385 6.585a2.1 2.1 0 0 0-2.97-2.97L9 12v3h3l8.385-8.415zM16 5l3 3"></path>
                    </g>
                    </svg>
                </button>          
                <i class="quote-star fas fa-star mb-2${starClass}" data-quote-id="${quote.id}" data-bs-toggle="tooltip" title="Star quote"></i>
                <i class="quote-delete fas fa-trash" data-quote-id="${quote.id}" data-bs-toggle="tooltip" title="Delete quote"></i>
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

        newCarouselItem.querySelectorAll("[data-bs-toggle='tooltip']").forEach(function (elem) {
            new bootstrap.Tooltip(elem);
        });

        newCarouselItem.querySelectorAll(".quote-star, .quote-delete, .quote-edit").forEach((icon) => {
            icon.addEventListener("click", function(e) {
                console.log("Icon clicked:", e.currentTarget);
                if (e.currentTarget.classList.contains('quote-star')) {
                    handleStarClick(e.currentTarget);
                }
                else if (e.currentTarget.classList.contains('quote-delete')) {
                    loadQuoteDeleteModal(e.currentTarget.getAttribute('data-quote-id'));
                }
                else if (e.currentTarget.classList.contains('quote-edit')) {
                    loadQuoteEditModal(e.currentTarget.getAttribute('data-quote-id'));
                }
            });
        });        
        newCarouselItem.querySelectorAll("[data-bs-toggle='tooltip']").forEach(function (elem) {
            new bootstrap.Tooltip(elem);
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
            starIcon.classList.toggle('starred');
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

function nextQuote() {
    quoteIndex = (quoteIndex + 1) % quotes.length;
    displayQuote(quoteIndex, false);
}

function prevQuote() {
    quoteIndex = (quoteIndex - 1 + quotes.length) % quotes.length;
    displayQuote(quoteIndex, false);
}

// Quotes of the day js
var qotd = [];
var qotdIndex = 0;
var timerQOTD = null;

async function getQOTD() {
    try {
        let response = await fetch('/get_quotes_of_the_day/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        let data = await response.json();

        if (!data.quotes) {
            throw new Error('Data does not contain quotes');
        }

        qotd = data.quotes;
        displayQOTD(0);
        startCarouselQOTD();
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
}

function displayQOTD(index) {
    let quote = qotd[index];

    let newCarouselItem = document.createElement('div');
    newCarouselItem.className = 'carousel-item';
    newCarouselItem.style.opacity = 0;
    newCarouselItem.innerHTML = `
        <div class="qotd-quote-card">
            <div class="qotd-content-wrapper mt-2">
                <div class="qotd-quote-content">
                    <p class="quote">"${quote.quote}" - ${quote.author}</p>
                </div>
            </div>
            <div class="qotd-icon-container">
                <i class="fas fa-save qotd-save-icon pb-4" title="Save quote" data-bs-toggle="tooltip" data-bs-placement="top"></i>
            </div>
        </div>`;

    newCarouselItem.querySelector('.qotd-save-icon').addEventListener('click', () => loadQOTDSaveModal(quote.id));

    let carouselInner = document.getElementById('qotd-carousel-inner');
    carouselInner.appendChild(newCarouselItem);

    let oldCarouselItems = Array.from(carouselInner.getElementsByClassName('carousel-item')).filter(item => item !== newCarouselItem);
    if (oldCarouselItems.length > 0) {
        oldCarouselItems.forEach(item => {
            item.style.opacity = 0;
            setTimeout(() => {
                if (carouselInner.contains(item)) {
                    carouselInner.removeChild(item);
                } else {
                    console.warn("Attempted to remove an element that is not a child of the carouselInner");
                }
            }, 1000);
        });
    }

    setTimeout(() => {
        newCarouselItem.style.opacity = 1;
        newCarouselItem.classList.add('active');
    }, oldCarouselItems.length > 0 ? 700 : 0);

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    });

}

async function saveQuote(quoteId) {
    let response = await fetch(`/qotd_save/${quoteId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // CSRF protection
        },
        body: JSON.stringify({quoteId: quoteId})
    });

    if (!response.ok) {
        console.error(`Network response was not ok: ${response.status} ${response.statusText}`);
        return;
    }

    let data = await response.json();
    let myModalEl = document.getElementById('quoteSaveModal');
    let bsModal = bootstrap.Modal.getInstance(myModalEl);
    bsModal.hide();

    if (data.success) {
        loadQuoteSavedModal(quoteId, data.author);
    } else {
        loadQuoteExistsModal(quoteId, data.message);
    }
}

function changeQOTD(index) {
    qotdIndex = index;
    displayQOTD(qotdIndex);
}

function startCarouselQOTD() {
    if (timerQOTD) {
        clearInterval(timerQOTD);
    }

    timerQOTD = setInterval(function () {
        changeQOTD((qotdIndex + 1) % qotd.length);
    }, 10000);
}

function nextQOTD() {
    changeQOTD((qotdIndex + 1) % qotd.length);
    startCarouselQOTD();
}

function prevQOTD() {
    changeQOTD((qotdIndex - 1 + qotd.length) % qotd.length);
    startCarouselQOTD();
}

window.addEventListener('load', function() {
    if (document.getElementById('savedQuotesCarousel')) {
        getQuotes();

        document.getElementById("savedQuotes-tab").addEventListener("click", async function() {
            await getQuotes();
        });
    
        document.querySelector('#savedQuotesCarousel .carousel-control-prev').addEventListener('click', function (e) {
            e.preventDefault();
            prevQuote();
        });
        document.querySelector('#savedQuotesCarousel .carousel-control-next').addEventListener('click', function (e) {
            e.preventDefault();
            nextQuote();
        });

        getQOTD();

        document.querySelector('#quoteOfDayCarouselSlideQOTD .carousel-control-prev').addEventListener('click', function (e) {
            e.preventDefault();
            prevQOTD();
        });
        document.querySelector('#quoteOfDayCarouselSlideQOTD .carousel-control-next').addEventListener('click', function (e) {
            e.preventDefault();
            nextQOTD();
        });

        updateTimerQOTD = setInterval(function() {
            clearInterval(timerQOTD);
            getQOTD();
        }, 3600000);
    }
});