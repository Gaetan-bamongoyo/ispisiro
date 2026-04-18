document.addEventListener("DOMContentLoaded", () => {

    // 1. Sticky Header
    const header = document.getElementById("header");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    });

    // 2. Mobile Menu Toggle
    const menuToggle = document.getElementById("menu-toggle");
    const navList = document.querySelector(".nav-list");

    menuToggle.addEventListener("click", () => {
        navList.classList.toggle("active");
        // Change icon
        const icon = menuToggle.querySelector("i");
        if (navList.classList.contains("active")) {
            icon.classList.remove("fa-bars");
            icon.classList.add("fa-times");
        } else {
            icon.classList.remove("fa-times");
            icon.classList.add("fa-bars");
        }
    });

    // 3. Mobile Dropdown Toggle
    const dropdowns = document.querySelectorAll(".dropdown");
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener("click", (e) => {
            if (window.innerWidth <= 992) {
                e.preventDefault();
                dropdown.classList.toggle("active");
            }
        });
    });

    // 4. Counters Animation (Intersection Observer)
    const counters = document.querySelectorAll(".counter");
    let speed = 200; // Animation speed

    const animateCounters = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const updateCount = () => {
                    const target = +counter.getAttribute('data-target');
                    const count = +counter.innerText;
                    
                    const inc = target / speed;

                    if (count < target) {
                        counter.innerText = Math.ceil(count + inc);
                        setTimeout(updateCount, 15);
                    } else {
                        counter.innerText = target;
                    }
                };

                updateCount();
                observer.unobserve(counter); // Only animate once
            }
        });
    };

    const counterObserver = new IntersectionObserver(animateCounters, {
        threshold: 0.5 // Trigger when 50% of the element is visible
    });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    // 5. Infinite Scrolling Carousel
    const scrollingTrack = document.getElementById("scrolling-track");
    if (scrollingTrack) {
        const content = scrollingTrack.innerHTML;
        scrollingTrack.innerHTML += content; // Clone cards for seamless loop
    }

});
