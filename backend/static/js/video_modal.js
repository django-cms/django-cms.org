/**
 * Video Modal - Desktop: modal, Mobile: native fullscreen
 * Supports both iframe embeds (YouTube/Vimeo) and local <video> files.
 */
(function() {
    'use strict';

    var MOBILE_BREAKPOINT = 768;

    function isMobile() {
        return window.innerWidth < MOBILE_BREAKPOINT;
    }

    function ensureHttps(url) {
        if (url && url.indexOf('//') === 0) {
            return 'https:' + url;
        }
        return url;
    }

    function openFullscreenEmbed(src) {
        var iframe = document.createElement('iframe');
        var fullSrc = ensureHttps(src);
        fullSrc += (fullSrc.indexOf('?') === -1 ? '?autoplay=1' : '&autoplay=1');
        iframe.src = fullSrc;
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
        iframe.referrerPolicy = 'no-referrer-when-downgrade';
        iframe.allowFullscreen = true;
        iframe.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:99999;border:none;background:#000;';
        document.body.appendChild(iframe);
        goFullscreen(iframe);
    }

    function openFullscreenVideo(src) {
        var video = document.createElement('video');
        video.src = src;
        video.controls = true;
        video.autoplay = true;
        video.playsInline = true;
        video.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:99999;background:#000;';
        document.body.appendChild(video);
        goFullscreen(video);
    }

    function goFullscreen(el) {
        var fsMethod = el.requestFullscreen || el.webkitRequestFullscreen || el.webkitEnterFullscreen;
        if (!fsMethod) {
            addCloseButton(el);
            return;
        }
        fsMethod.call(el).then(function() {
            document.addEventListener('fullscreenchange', function onExit() {
                if (!document.fullscreenElement) {
                    document.removeEventListener('fullscreenchange', onExit);
                    el.remove();
                }
            });
        }).catch(function() {
            addCloseButton(el);
        });
    }

    function addCloseButton(el) {
        var closeBtn = document.createElement('button');
        closeBtn.textContent = '\u2715';
        closeBtn.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:100000;background:rgba(0,0,0,0.6);color:#fff;border:none;font-size:2rem;width:48px;height:48px;border-radius:50%;cursor:pointer;';
        document.body.appendChild(closeBtn);
        closeBtn.addEventListener('click', function() {
            if (el.pause) el.pause();
            el.remove();
            closeBtn.remove();
        });
    }

    function getModalMedia(modal) {
        var iframe = modal.querySelector('iframe[data-src]');
        if (iframe) return { type: 'iframe', el: iframe, src: iframe.dataset.src };
        var video = modal.querySelector('video[data-src]');
        if (video) return { type: 'video', el: video, src: video.dataset.src };
        return null;
    }

    function initVideoModals() {
        // Desktop modal: lazy load media on open, stop on close
        document.querySelectorAll('.modal[id^="videoModal-"]').forEach(function(modal) {
            var media = getModalMedia(modal);
            if (!media) return;

            modal.addEventListener('shown.bs.modal', function() {
                if (media.type === 'iframe') {
                    media.el.src = ensureHttps(media.src);
                } else {
                    media.el.src = media.src;
                    media.el.play();
                }
            });

            modal.addEventListener('hidden.bs.modal', function() {
                if (media.type === 'video') {
                    media.el.pause();
                    media.el.currentTime = 0;
                }
                media.el.removeAttribute('src');
                media.el.load();
            });
        });

        // Poster click handler
        document.querySelectorAll('.video-poster-wrapper[data-video-target]').forEach(function(poster) {
            poster.addEventListener('click', function() {
                var modalSelector = poster.dataset.videoTarget;
                var modal = document.querySelector(modalSelector);
                if (!modal) return;

                var media = getModalMedia(modal);
                if (!media) return;

                if (isMobile()) {
                    if (media.type === 'iframe') {
                        openFullscreenEmbed(media.src);
                    } else {
                        openFullscreenVideo(media.src);
                    }
                } else {
                    var bsModal = bootstrap.Modal.getOrCreateInstance(modal);
                    bsModal.show();
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVideoModals);
    } else {
        initVideoModals();
    }

    if (window.CMS) {
        window.CMS.$(window).on('cms-content-refresh', initVideoModals);
    }
})();
