/**
 * Counter Animation with Intersection Observer
 * Animates counter numbers only when they become visible in the viewport
 * Supports accessibility features (reduced motion, screen readers)
 */

(function() {
    'use strict';

    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Format number with comma as thousand separator
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // Animate a single counter
    function animateCounter(counter) {
        // Check if already animated
        if (counter.classList.contains('counter-animated')) {
            return;
        }

        const target = parseInt(counter.getAttribute('data-target'), 10);

        // Validate target number
        if (isNaN(target)) {
            console.warn('Counter has invalid data-target:', counter);
            return;
        }

        // Mark as animated to prevent duplicate animations
        counter.classList.add('counter-animated');

        // If user prefers reduced motion, show final value immediately
        if (prefersReducedMotion) {
            counter.innerText = formatNumber(target);
            counter.setAttribute('aria-live', 'off');
            return;
        }

        // Announce to screen readers that counting is starting
        counter.setAttribute('aria-live', 'polite');

        let count = 0;
        const duration = 2000; // Animation duration in ms
        const increment = target / (duration / 16); // ~60fps
        const startTime = performance.now();

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function for smoother animation (easeOutExpo)
            const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

            count = Math.floor(easeProgress * target);
            counter.innerText = formatNumber(count);

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                // Ensure final value is exact
                counter.innerText = formatNumber(target);
                // Stop announcing updates to screen readers
                counter.setAttribute('aria-live', 'off');
            }
        };

        requestAnimationFrame(updateCounter);
    }

    // Initialize Intersection Observer
    function initCounterObserver() {
        const counters = document.querySelectorAll('.counter-number');

        if (counters.length === 0) {
            return;
        }

        // Create Intersection Observer
        const observerOptions = {
            root: null, // viewport
            rootMargin: '0px',
            threshold: 0.5 // Trigger when 50% of element is visible
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    // Unobserve after animation starts (one-time animation)
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all counters
        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCounterObserver);
    } else {
        // DOM already loaded
        initCounterObserver();
    }
})();
