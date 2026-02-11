/**
 * Quote Slider
 *
 * Initializes Swiper on .quote-slider containers.
 * Always active (desktop and mobile) when there are 2+ quote items.
 */

(function () {
	'use strict';

	function initQuoteSliders() {
		if (typeof Swiper === 'undefined') {
			console.error('Swiper library not loaded!');
			return;
		}

		document.querySelectorAll('.quote-slider').forEach(function (container) {
			var swiperEl = container.querySelector('.quote-swiper');
			if (!swiperEl) return;

			var prevBtn = container.querySelector('.quote-slider-prev');
			var nextBtn = container.querySelector('.quote-slider-next');

			new Swiper(swiperEl, {
				slidesPerView: 1,
				spaceBetween: 20,
				loop: true,
				navigation: {
					nextEl: nextBtn,
					prevEl: prevBtn
				},
				keyboard: {
					enabled: true,
					onlyInViewport: true
				}
			});
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initQuoteSliders);
	} else {
		initQuoteSliders();
	}
})();
