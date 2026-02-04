// Navbar Mega Menu - Backdrop Management

document.addEventListener('DOMContentLoaded', function() {
  // create backdrop element
  const backdrop = document.createElement('div');
  backdrop.className = 'dropdown-backdrop';
  document.body.appendChild(backdrop);

  // All dropdowns in the navbar
  const dropdowns = document.querySelectorAll('.navbar .dropdown');

  // Check if viewport is desktop (min-width: 1200px)
  function isDesktop() {
    return window.matchMedia('(min-width: 1200px)').matches;
  }

  function hideBackdrop() {
    backdrop.classList.remove('show');
  }

  function closeAllDropdowns() {
    dropdowns.forEach(dropdown => {
      const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
      if (toggle) {
        // Remove active class from toggle
        toggle.classList.remove('active');
        
        if (toggle.getAttribute('aria-expanded') === 'true') {
          const bsDropdown = bootstrap.Dropdown.getInstance(toggle) ||
            bootstrap.Dropdown.getOrCreateInstance(toggle);
          bsDropdown.hide();
        }
      }
    });
  }

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
    if (!toggle) return;

    // If dropdown is shown
    toggle.addEventListener('show.bs.dropdown', function() {
      // Only show backdrop on desktop
      if (isDesktop()) {
        backdrop.classList.add('show');
        toggle.classList.add('active');
      }
    });

    // if dropdown is hidden
    toggle.addEventListener('hide.bs.dropdown', function() {
      // Remove active class from toggle
      toggle.classList.remove('active');
      
      // Only handle backdrop on desktop
      if (isDesktop()) {
        // Check if any other dropdown is still open
        setTimeout(() => {
          const anyOpen = Array.from(dropdowns).some(dd => {
            const ddToggle = dd.querySelector('[data-bs-toggle="dropdown"]');
            return ddToggle && ddToggle.getAttribute('aria-expanded') === 'true';
          });

          // Only hide backdrop if no dropdown is open
          if (!anyOpen) {
            backdrop.classList.remove('show');
          }
        }, 0);
      }
    });
  });

  // Mark dropdown links as active if they match the current URL
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar .dropdown-menu a[href]').forEach(link => {
    const linkPath = link.getAttribute('href');
    if (linkPath && linkPath !== '#' && currentPath.startsWith(linkPath)) {
      link.classList.add('active');
    }
  });

  // Backdrop closes dropdown on click
  backdrop.addEventListener('click', function() {
    closeAllDropdowns();
    hideBackdrop();
  });

  // Resize handler: close dropdowns when crossing 1199px threshold
  let resizeTimeout;

  function handleResize() {
    // If viewport is 1199px or smaller, close everything
    if (window.innerWidth <= 1199) {
      closeAllDropdowns();
      hideBackdrop();
    }
  }

  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(handleResize, 100);
  });
});