// Navbar Mega Menu - Backdrop Management

document.addEventListener('DOMContentLoaded', function() {
  // create backdrop element
  const backdrop = document.createElement('div');
  backdrop.className = 'dropdown-backdrop';
  document.body.appendChild(backdrop);

  // All dropdowns in the navbar
  const dropdowns = document.querySelectorAll('.navbar .dropdown');

  // Check if viewport is desktop (min-width: 1199.98px)
  function isDesktop() {
    return window.matchMedia('(min-width: 1199.98px)').matches;
  }

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
    if (!toggle) return;

    // If dropdown is shown
    toggle.addEventListener('show.bs.dropdown', function() {
      // Only show backdrop on desktop
      if (isDesktop()) {
        backdrop.classList.add('show');
      }
    });

    // if dropdown is hidden
    toggle.addEventListener('hide.bs.dropdown', function() {
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
    // Close all open dropdowns
    dropdowns.forEach(dropdown => {
      const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
      if (toggle && toggle.getAttribute('aria-expanded') === 'true') {
        const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
        if (bsDropdown) {
          bsDropdown.hide();
        }
      }
    });
  });
});
