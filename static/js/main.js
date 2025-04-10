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

});


