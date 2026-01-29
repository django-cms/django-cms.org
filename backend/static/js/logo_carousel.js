/**
 *
 * Swiper config
 */

(function() {
	'use strict';

	function initSwiper() {

		if (typeof Swiper === 'undefined') {
			console.error('Swiper library not loaded!');
			return;
		}

		try {
			const swiperElements = document.querySelectorAll('.logo-swiper-carousel');

			if (swiperElements.length === 0) {
				return;
			}

			swiperElements.forEach(elem => {
				const loop = (elem.dataset.loop) === 'true';
				const spaceBetweenSlides = parseInt(elem.dataset.spaceBetweenSlides) || 20;
				const delay = parseInt(elem.dataset.delay) || 3000;
				const autoplay = (elem.dataset.autoplay === 'true')
					? {delay: delay, disableOnInteraction: false}
					: false;

				new Swiper(`.logoSwiper-${elem.dataset.instanceId}`, {
					slidesPerView: 1,      // Mobile
					spaceBetween: spaceBetweenSlides,
					loop: loop,
					keyboard: {
						enabled: true,
						onlyInViewport: true,
					},
					autoplay: autoplay,
					navigation: {
						nextEl: `.btn-next-${elem.dataset.instanceId}`,
						prevEl: `.btn-prev-${elem.dataset.instanceId}`,
					},
					breakpoints: {
						768: {
							slidesPerView: 3, // Tablet
							spaceBetween: spaceBetweenSlides
						},
						1024: {
							slidesPerView: 4, // Desktop
							spaceBetween: spaceBetweenSlides
						}
					}
				});
			});
		} catch (e) {
			console.error("Error initializing Swiper instance", e);
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initSwiper);
	} else {
		initSwiper();
	}

})();
