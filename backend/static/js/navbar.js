// Navbar Mega Menu - Backdrop Management

document.addEventListener('DOMContentLoaded', function() {
  // create backdrop element
  const backdrop = document.createElement('div');
  backdrop.className = 'dropdown-backdrop';
  document.body.appendChild(backdrop);

  // All dropdowns in the navbar
  const dropdowns = document.querySelectorAll('.navbar .dropdown');

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
    if (!toggle) return;

    // If dropdown is shown
    toggle.addEventListener('show.bs.dropdown', function() {
      backdrop.classList.add('show');
    });

    // if dropdown is hidden
    toggle.addEventListener('hide.bs.dropdown', function() {
      backdrop.classList.remove('show');
    });
  });

  // Backdrop closes dropdown on click
  backdrop.addEventListener('click', function() {
    console.log('Backdrop clicked');
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
