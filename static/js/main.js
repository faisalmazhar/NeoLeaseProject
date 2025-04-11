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
  const arrowLeft = document.querySelector('.arrow-left');
  const arrowRight = document.querySelector('.arrow-right');
  const bigImage = document.getElementById('carousel-big-image');

  if (singleImageWrapper && bigImage && arrowLeft && arrowRight) {
    // Pull the CSV of image URLs from data attr
    const imageUrls = singleImageWrapper.dataset.imageUrls
      ? singleImageWrapper.dataset.imageUrls.split(',')
      : [];

    // If there's more than 1 image, let user cycle
    if (imageUrls.length > 1) {
      let currentIndex = 0;

      function updateBigImage() {
        bigImage.src = imageUrls[currentIndex];
      }

      arrowLeft.addEventListener('click', () => {
        if (currentIndex > 0) {
          currentIndex--;
          updateBigImage();
        }
      });

      arrowRight.addEventListener('click', () => {
        if (currentIndex < imageUrls.length - 1) {
          currentIndex++;
          updateBigImage();
        }
      });
    } else {
      // If only 0 or 1 images, hide arrows
      arrowLeft.style.display = 'none';
      arrowRight.style.display = 'none';
    }
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
  

});


