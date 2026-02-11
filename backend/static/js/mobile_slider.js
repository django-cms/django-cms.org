/**
 * Mobile Slider
 *
 * Converts any container with class "mobile-slider" into a Swiper carousel
 * below the md breakpoint (768px) when there are 2 or more direct children.
 * Above md, the normal grid layout is restored.
 */

(function () {
	'use strict';

	const MD_BREAKPOINT = 768;

	function initMobileSliders() {
		if (typeof Swiper === 'undefined') {
			console.error('Swiper library not loaded!');
			return;
		}

		const containers = document.querySelectorAll('.mobile-slider');
		const sliderInstances = [];

		containers.forEach(function (container) {
			const gridEl = container.querySelector('[class*="grid-"], .row');
			if (!gridEl) return;

			const children = Array.from(gridEl.children);
			if (children.length < 2) return;

			let swiperInstance = null;
			let isSliderActive = false;

			// Create navigation wrapper with buttons
			const navWrapper = document.createElement('div');
			navWrapper.className = 'mobile-slider-nav';

			const navPrev = document.createElement('button');
			navPrev.className = 'mobile-slider-btn mobile-slider-prev';
			navPrev.setAttribute('aria-label', 'Previous slide');
			navPrev.innerHTML = '<i class="bi bi-chevron-left"></i>';

			const navNext = document.createElement('button');
			navNext.className = 'mobile-slider-btn mobile-slider-next';
			navNext.setAttribute('aria-label', 'Next slide');
			navNext.innerHTML = '<i class="bi bi-chevron-right"></i>';

			navWrapper.appendChild(navPrev);
			navWrapper.appendChild(navNext);

			function activateSlider() {
				if (isSliderActive) return;

				// Add swiper class to grid element
				gridEl.classList.add('swiper');

				// Wrap children in swiper-wrapper and swiper-slide
				const wrapper = document.createElement('div');
				wrapper.className = 'swiper-wrapper';

				children.forEach(function (child) {
					const slide = document.createElement('div');
					slide.className = 'swiper-slide';
					slide.appendChild(child);
					wrapper.appendChild(slide);
				});

				// appendChild already removes children from gridEl, no need to clear
				gridEl.appendChild(wrapper);

				// Insert nav wrapper above the grid
				gridEl.parentNode.insertBefore(navWrapper, gridEl);

				swiperInstance = new Swiper(gridEl, {
					slidesPerView: 1,
					spaceBetween: 20,
					loop: true,
					navigation: {
						nextEl: navNext,
						prevEl: navPrev
					},
					keyboard: {
						enabled: true,
						onlyInViewport: true
					}
				});

				isSliderActive = true;
			}

			function deactivateSlider() {
				if (!isSliderActive) return;

				if (swiperInstance) {
					swiperInstance.destroy(true, true);
					swiperInstance = null;
				}

				// Remove nav wrapper from DOM
				if (navWrapper.parentNode) navWrapper.parentNode.removeChild(navWrapper);

				// Remove swiper structure without destroying event listeners
				while (gridEl.firstChild) {
					gridEl.removeChild(gridEl.firstChild);
				}
				gridEl.classList.remove('swiper');

				children.forEach(function (child) {
					gridEl.appendChild(child);
				});

				isSliderActive = false;
			}

			function handleResize() {
				if (window.innerWidth < MD_BREAKPOINT) {
					activateSlider();
				} else {
					deactivateSlider();
				}
			}

			// Initial check
			handleResize();

			sliderInstances.push({ handleResize: handleResize });
		});

		// Single debounced resize listener for all slider instances
		let resizeTimer;
		window.addEventListener('resize', function () {
			clearTimeout(resizeTimer);
			resizeTimer = setTimeout(function () {
				sliderInstances.forEach(function (instance) {
					instance.handleResize();
				});
			}, 150);
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initMobileSliders);
	} else {
		initMobileSliders();
	}
})();
