// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {

  // ========== 1) Scroll-down arrow on hero section ==========
  const scrollArrow = document.querySelector(".scroll-down");
  if (scrollArrow) {
    scrollArrow.addEventListener("click", () => {
      window.scrollTo({
        top: window.innerHeight,
        behavior: "smooth"
      });
    });
  }

  // ========== 2) Hamburger nav toggle ==========
  const navToggle = document.querySelector('.nav-toggle');
  const mainNav = document.querySelector('.main-nav');

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      mainNav.classList.toggle('nav-open');
    });
  }

  // ========== 3) Fade out hero text on scroll ==========
  const heroContent = document.querySelector('.hero-content');
  window.addEventListener('scroll', () => {
    if (!heroContent) return;
    const scrolled = window.scrollY;
    const fadeLimit = 200;

    if (scrolled < fadeLimit) {
      heroContent.style.opacity = 1 - (scrolled / fadeLimit);
    } else {
      heroContent.style.opacity = 0;
    }
  });

  
// ========== 4) Single-image carousel logic ==========
const singleImageWrapper = document.querySelector('.carousel-single-image');
const arrowLeft  = document.querySelector('.arrow-left');
const arrowRight = document.querySelector('.arrow-right');
const bigImage   = document.getElementById('carousel-big-image');
const spinner    = document.getElementById('img-spinner');   // the <div class="spinner">

if (singleImageWrapper && bigImage && arrowLeft && arrowRight) {
  // 1) collect URLs
  const imageUrls = singleImageWrapper.dataset.imageUrls
        ? singleImageWrapper.dataset.imageUrls.split(',')
        : [];

  if (!imageUrls.length) {
    arrowLeft.style.display = 'none';
    arrowRight.style.display = 'none';
    return;
  }

  let currentIndex = 0;

  // helper: try to load a URL; on 404 drop it and recurse
  function loadImage(idx) {
    if (idx < 0 || idx >= imageUrls.length) return;      // safety
    spinner.style.display = 'block';
    bigImage.onload  = () => { spinner.style.display = 'none'; };
    bigImage.onerror = () => {
      // remove bad URL and try again (same index now points to next img)
      imageUrls.splice(idx, 1);
      if (imageUrls.length) loadImage(idx >= imageUrls.length ? idx - 1 : idx);
      else { spinner.style.display = 'none'; bigImage.style.display = 'none'; }
    };
    bigImage.src = imageUrls[idx];
    currentIndex = idx;
  }

  // initial display
  loadImage(0);

  // arrow handlers
  arrowLeft.onclick  = () => loadImage(currentIndex - 1);
  arrowRight.onclick = () => loadImage(currentIndex + 1);
}


  
  
  
  // Simple Cookie Banner Logic
    const banner = document.getElementById('cookie-banner');
    if (banner) {
      // Check localStorage or cookies to see if user made a choice
      const cookieChoice = localStorage.getItem('cookie_choice');
      if (!cookieChoice) {
        banner.style.display = 'block';
      }
  
      document.getElementById('cookie-accept').addEventListener('click', () => {
        localStorage.setItem('cookie_choice', 'accepted');
        banner.style.display = 'none';
      });
  
      document.getElementById('cookie-decline').addEventListener('click', () => {
        localStorage.setItem('cookie_choice', 'declined');
        banner.style.display = 'none';
      });
  
      // document.getElementById('cookie-settings').addEventListener('click', () => {
      //   // TODO: Show a popup or some advanced settings?
      //   alert('Hier kun je later een popup maken om cookie-instellingen aan te passen.');
      // });
    }
    
    const favButtons = document.querySelectorAll('.favorite-btn');
    favButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const carId = btn.getAttribute('data-car-id');
        const title = btn.getAttribute('data-title');
        const imageUrl = btn.getAttribute('data-image') || "";
        const monthly = btn.getAttribute('data-monthly') || "";
        addToFavorites(carId, title, imageUrl, monthly);
      });
    });

  
  /** 
   * addToFavorites: store in localStorage
   */
  function addToFavorites(id, title, imageUrl, monthlyPayment) {
    // 1) get or create "favorites" array from localStorage
    let stored = localStorage.getItem("favorites");
    let favorites = [];
    if (stored) {
      try {
        favorites = JSON.parse(stored);
      } catch(e) {
        console.warn("Could not parse favorites:", e);
        favorites = [];
      }
    }
  
    // 2) Check if already in favorites
    const exists = favorites.find(item => item.id == id);
    if (exists) {
      alert("Deze auto is al in je favorieten!");
      return;
    }
  
    // 3) Otherwise push new object
    favorites.push({
      id: id,
      title: title,
      imageUrl: imageUrl,
      monthlyPayment: monthlyPayment
    });
  
    // 4) Save
    localStorage.setItem("favorites", JSON.stringify(favorites));
  
    alert("Toegevoegd aan favorieten!");

    }
  


  // 4) Slider on home page

  $(document).ready(function() {
    $('.logo-slider').slick({
      infinite: true,
      slidesToShow: 6,   // Show 6 logos at once (on big screens)
      slidesToScroll: 1,
      autoplay: true,
      autoplaySpeed: 2000,
      arrows: false,     
      // If your images come in super large, you can set variableWidth to false 
      // and let them auto-size by your CSS:
      variableWidth: false,  
      responsive: [
        {
          breakpoint: 992,  
          settings: { slidesToShow: 4 }
        },
        {
          breakpoint: 768,  
          settings: { slidesToShow: 3 }
        },
        {
          breakpoint: 480,
          settings: { slidesToShow: 2 }
        }
      ]
    });
  });

  $('.featured-cars-marquee').slick({
    infinite: true,
    slidesToShow: 4,       // number of car cards visible at once
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 0,      // set to 0 for continuous marquee style
    speed: 8000,           // overall scrolling speed
    // cssEase: 'linear',     // constant speed
    arrows: true,         // hide next/prev arrows
    pauseOnHover: true,
    variableWidth: false,   // let each card have its own width
    responsive: [
      {
        breakpoint: 992,
        settings: { slidesToShow: 2 }
      },
      {
        breakpoint: 768,
        settings: { slidesToShow: 1 }
      }
    ]
  });
  


  const slides = document.querySelectorAll('.hero-slide');

  // This ensures the first slide is visible by default
  if (slides && slides.length > 0) {
    let currentSlide = 0;


    slides[currentSlide].classList.add('active');
    
    // Rotate every 1.5 seconds
    const intervalTime = 2500;  // in milliseconds

    setInterval(() => {
      // fade out the current slide
      slides[currentSlide].classList.remove('active');
      
      // move to the next
      currentSlide = (currentSlide + 1) % slides.length;
      
      // fade the new one in
      slides[currentSlide].classList.add('active');
    }, intervalTime);
  }

  
  
  // ========== 7) “General Calculator” (calculator_general.html) logic ==========
  // We detect if those calculator inputs exist; if yes, we do the logic:
  const purchasePriceInput = document.getElementById('purchasePrice');
  const downPaymentInput   = document.getElementById('downPayment');
  const balloonInput       = document.getElementById('balloon');
  const monthsRange        = document.getElementById('monthsRange');
  const monthsValueLabel   = document.getElementById('monthsValue');
  const monthlyPaymentEl   = document.getElementById('monthlyPayment');
  const errorBox           = document.getElementById('errorBox');
  const applyBtn           = document.getElementById('applyNowBtn');

  // Only run the calc if we see the #purchasePrice field (i.e. on that page)
  if (purchasePriceInput) {

    function recalc() {
      const purchase = parseFloat(purchasePriceInput.value) || 30000;
      const down     = parseFloat(downPaymentInput.value)   || 5000;
      const balloon  = parseFloat(balloonInput.value)       || 10000;
      const months   = parseInt(monthsRange.value)          || 60;

      // financed = (purchase - down - balloon)
      const financed = purchase - down - balloon;
      const monthlyRate = 0.0083;   // ~10% APR => 0.83% per month
      const interestPart = financed * monthlyRate;
      const principalPart = financed / months;
      const totalMonth = interestPart + principalPart;

      // 1) If balloon is bigger than (purchase - down), show error
      if (balloon > (purchase - down)) {
        if (errorBox) {
          errorBox.style.display = 'block';
          errorBox.textContent = "De slottermijn mag niet hoger zijn dan het te financieren bedrag!";
        }
        if (applyBtn) applyBtn.disabled = true;
        if (monthlyPaymentEl) monthlyPaymentEl.textContent = "€---";
        return;
      }

      // 2) If totalMonth < 0 => negative monthly => error
      if (totalMonth < 0) {
        if (errorBox) {
          errorBox.style.display = 'block';
          errorBox.textContent = "Ongeldige invoer: maandbedrag kan niet negatief zijn!";
        }
        if (applyBtn) applyBtn.disabled = true;
        if (monthlyPaymentEl) monthlyPaymentEl.textContent = "€---";
        return;
      }

      // Otherwise, no error => hide error, update monthly
      if (errorBox) errorBox.style.display = 'none';
      if (applyBtn) applyBtn.disabled = false;
      if (monthlyPaymentEl) {
        const finalVal = totalMonth.toFixed(2);
        monthlyPaymentEl.textContent = "€" + finalVal;
      }
      if (monthsValueLabel) {
        monthsValueLabel.textContent = months;
      }
    }

    purchasePriceInput.addEventListener('input', recalc);
    downPaymentInput.addEventListener('input', recalc);
    balloonInput.addEventListener('input', recalc);
    monthsRange.addEventListener('input', recalc);

    recalc();

    if (applyBtn) {
      applyBtn.addEventListener('click', () => {
        window.location.href = "/contact";
      });
    }
  }

  const selects = document.querySelectorAll('.brandSelect');

  selects.forEach((select) => {
    new Choices(select, {
      searchEnabled: true,         // enable search if you want
      itemSelectText: '',          // remove redundant text "Press to select"
      shouldSort: false,           // keep original order
      placeholder: true,           // enable placeholder
      allowHTML: false,
      maxItemCount: 5,
      classNames: {
        containerOuter: 'choices',
        containerInner: 'choices__inner',
        input: 'choices__input',
        inputCloned: 'choices__input--cloned',
        list: 'choices__list',
        listItems: 'choices__list--multiple',
        listSingle: 'choices__list--single',
        listDropdown: 'choices__list--dropdown',
        item: 'choices__item',
        itemSelectable: 'choices__item--selectable',
        itemDisabled: 'choices__item--disabled',
        itemChoice: 'choices__item--choice',
        placeholder: 'choices__placeholder',
        group: 'choices__group',
        groupHeading: 'choices__heading',
        button: 'choices__button',
        activeState: 'is-active',
        focusState: 'is-focused',
        openState: 'is-open',
        disabledState: 'is-disabled',
        highlightedState: 'is-highlighted',
        selectedState: 'is-selected',
        flippedState: 'is-flipped',
        loadingState: 'is-loading',
        noResults: 'has-no-results',
        noChoices: 'has-no-choices'
      },
    });
  });





});


