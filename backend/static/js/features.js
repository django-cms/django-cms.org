/**
 * Features Section - Accordion Image Sync
 * Synchronizes accordion item expansion with corresponding images
 */

(function() {
    'use strict';

    function initFeaturesAccordion() {
        const featuresSections = document.querySelectorAll('.features-section');

        featuresSections.forEach(section => {
            const accordion = section.querySelector('.features-accordion .accordion');
            const images = section.querySelectorAll('.features-image');

            if (!accordion || images.length === 0) {
                return;
            }

            // Show image corresponding to the open accordion item
            // Check if any image already has the active class from the template
            const hasActiveImage = Array.from(images).some(img => img.classList.contains('active'));

            if (!hasActiveImage) {
                // No active image set, find the open accordion item
                const openItem = accordion.querySelector('.accordion-collapse.show');
                if (openItem) {
                    // Find the index of the open accordion item
                    const accordionItems = accordion.querySelectorAll('.accordion-item');
                    const openIndex = Array.from(accordionItems).findIndex(item =>
                        item.querySelector('.accordion-collapse.show')
                    );
                    if (openIndex !== -1 && images[openIndex]) {
                        images[openIndex].classList.add('active');
                    }
                } else if (images[0]) {
                    // Fallback to first image if no item is open
                    images[0].classList.add('active');
                }
            }

            // Listen to accordion events
            const accordionItems = accordion.querySelectorAll('.accordion-item');
            let isOpeningNewItem = false;

            accordionItems.forEach((item, index) => {
                const collapse = item.querySelector('.accordion-collapse');
                const button = item.querySelector('.accordion-button');

                if (!collapse || !button) return;

                // Override Bootstrap's default transition speed
                window.bootstrap.Collapse.getOrCreateInstance(collapse, {
                    toggle: false
                });

                // Track when we're about to open an item
                collapse.addEventListener('show.bs.collapse', () => {
                    isOpeningNewItem = true;
                });

                // Prevent closing the currently open item unless another is opening
                collapse.addEventListener('hide.bs.collapse', (e) => {
                    if (!isOpeningNewItem) {
                        // No other item is being opened, prevent closing this one
                        e.preventDefault();
                        e.stopPropagation();
                    }
                });

                // Reset flag and switch image after accordion is fully opened
                collapse.addEventListener('shown.bs.collapse', () => {
                    isOpeningNewItem = false;
                    // Switch image after accordion is fully opened
                    images.forEach(img => img.classList.remove('active'));
                    if (images[index]) {
                        images[index].classList.add('active');
                    }
                });
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFeaturesAccordion);
    } else {
        initFeaturesAccordion();
    }

    // Re-initialize when CMS plugins are added/edited (for edit mode)
    if (window.CMS) {
        window.CMS.$(window).on('cms-content-refresh', initFeaturesAccordion);
    }
})();
