// Navbar Mega Menu - Backdrop für geöffnetes Dropdown

document.addEventListener('DOMContentLoaded', function() {
  // Warte bis Bootstrap geladen ist
  if (typeof bootstrap === 'undefined') {
    console.error('Bootstrap ist nicht geladen!');
    return;
  }

  // Backdrop-Element erstellen
  const backdrop = document.createElement('div');
  backdrop.className = 'dropdown-backdrop';
  document.body.appendChild(backdrop);

  // Alle Dropdowns in der Navbar
  const dropdowns = document.querySelectorAll('.navbar .dropdown');

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
    if (!toggle) return;

    // Wenn Dropdown geöffnet wird
    toggle.addEventListener('show.bs.dropdown', function() {
      console.log('Dropdown öffnet sich');
      backdrop.classList.add('show');
    });

    // Wenn Dropdown geschlossen wird
    toggle.addEventListener('hide.bs.dropdown', function() {
      console.log('Dropdown schließt sich');
      backdrop.classList.remove('show');
    });
  });

  // Backdrop schließt Dropdown beim Klick
  backdrop.addEventListener('click', function() {
    console.log('Backdrop geklickt');
    // Schließe alle offenen Dropdowns
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
