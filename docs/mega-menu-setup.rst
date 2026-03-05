=====================
Mega Menu Setup Guide
=====================

This guide explains how to create a mega menu dropdown for your navigation using django CMS pages with aliases.

Overview
========

The mega menu system uses django CMS's page hierarchy combined with djangocms-alias to create rich, customizable dropdown menus in your navigation bar.

Prerequisites
=============

- django CMS installed and configured
- djangocms-alias installed
- Bootstrap 5 (for styling)

Step-by-Step Setup
==================

1. Create a Parent Page with Reverse ID
----------------------------------------

To enable a dropdown mega menu for a navigation item:

1. **Create or edit a page** that should appear in the navigation with a dropdown
2. **Enable "In Navigation"** in the page settings so it appears in the menu
3. **Go to Advanced Settings** of the page
4. **Set a Reverse ID** – this is the identifier used to link the page to its mega menu alias

**Example:**

- Page Title: "About Django CMS"
- Reverse ID: ``about`` (use lowercase, no spaces)

.. note::
   The reverse ID must be unique across your site. A page does **not** need child pages to show a dropdown –
   having a reverse ID is sufficient to trigger the dropdown behavior.

2. Visit the Page to Auto-Create the Alias
-------------------------------------------

Once the reverse ID is set and the page is visited (by a logged-in staff member or publicly, depending on
whether versioning is enabled), the ``{% static_alias %}`` template tag **automatically creates** an empty
alias named ``mega-menu-[reverse-id]``.

- For the example above: ``mega-menu-about``

You do not need to manually create the alias in the admin beforehand.

3. Edit the Alias Content
--------------------------

After the alias has been auto-created:

1. **Go to Aliases** in your django CMS admin (or use the frontend editor)
2. **Find the alias** named ``mega-menu-[reverse-id]``
3. **Add plugins** to the alias placeholder to build your mega menu content

   - You can use any plugins: Text, Images, Links, Cards, etc.
   - Use Bootstrap grid classes for layout (``row``, ``col-lg-4``, etc.)

4. **Publish** the alias

4. How It Works
----------------

The system automatically connects pages to their mega menus:

1. **Navigation rendering** checks if a page has child pages **or** a reverse ID
2. **If either condition is true**, the page renders as a dropdown toggle
3. **If a reverse ID exists**, the template loads the alias: ``mega-menu-[reverse-id]``
4. **If the alias doesn't exist yet**, it is created automatically on first page visit
5. **If no reverse ID** but child pages exist, a simple dropdown with links to children is shown instead

5. Template Structure
----------------------

The menu template ([menu/menu.html](backend/templates/menu/menu.html)) handles this logic:

.. code-block:: django

   {% if child.children or child.attr.reverse_id %}
     <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown">
       {{ child.get_menu_title }}
     </a>

     <div class="dropdown-menu">
       {% if child.attr.reverse_id %}
         {# Load (or auto-create) mega menu alias #}
         {% with "mega-menu-"|add:child.attr.reverse_id as alias_code %}
           {% static_alias alias_code %}
         {% endwith %}
       {% else %}
         {# Fallback: render simple dropdown with child page links #}
         {% include "menu/dropdown.html" with parent=child only %}
       {% endif %}
     </div>
   {% endif %}

Example: Creating an "About" Mega Menu
=======================================

Page Setup
----------

1. Create a page titled "About Django CMS"
2. Enable "In Navigation"
3. Set Reverse ID: ``about``
4. Publish the page

Alias Setup
-----------

1. Visit the page once (as a logged-in staff member) – the alias ``mega-menu-about`` is created automatically
2. Open the alias in the admin or frontend editor
3. Add content structure, for example:

   .. code-block:: text

      - Row Plugin
        - Column (col-lg-4)
          - Text Plugin: "Who we serve"
          - Text Plugin: Description
          - TextLink Plugin
        - Column (col-lg-4)
          - Heading Plugin: Title for links
          - LinksContainer
        - Column (col-lg-4)
          - Card Plugin
            - Card header
              - Heading Plugin
            - Card body
              - Text Plugin
            - Card footer
              - TextLink Plugin

4. Publish the alias

Result
------

The "About Django CMS" menu item will now show a rich mega menu with your custom content when hovered or clicked.

Fallback Behavior
=================

If a page has a reverse ID but the alias has not been edited yet (empty), the dropdown will appear but show
no content until plugins are added to the alias.

If a page has no reverse ID but has child pages, the system automatically falls back to rendering a simple
dropdown menu with links to the child pages.

Styling
=======

The mega menu uses Bootstrap 5 dropdown components with custom styling:

- **Desktop**: Full-width dropdown with backdrop overlay
- **Mobile**: Collapsible accordion-style menu
- **Animations**: Smooth fade-in and slide effects

Styles are defined in ``static/scss/_navbar.scss`` with a mobile-first approach.

Tips
====

1. **Keep reverse IDs simple**: Use lowercase, no spaces (e.g., ``about``, ``services``, ``products``)
2. **No child pages needed**: A page with only a reverse ID is enough to trigger the mega menu dropdown
3. **Use Bootstrap grid**: Organize mega menu content with Bootstrap's grid system
4. **Test responsive**: Ensure your mega menu works on all screen sizes
5. **Reuse aliases**: You can use the same alias for multiple pages if needed

Troubleshooting
===============

Mega menu not showing
---------------------

- Verify the reverse ID is set on the page
- Make sure the page is enabled in navigation
- Ensure the alias is published (if versioning is enabled)
- Check that the alias name matches: ``mega-menu-[reverse-id]``

Alias not auto-created
----------------------

- If versioning is enabled, the alias is only auto-created when a **logged-in staff member** visits the page
- Unauthenticated visitors will not trigger alias creation when versioning is active

Content not displaying
----------------------

- Make sure plugins are added to the alias placeholder
- Check that the alias is published
- Clear django CMS cache if needed

Styling issues
--------------

- Compile SCSS: ``npm run build`` or your build command
- Check browser console for JavaScript errors
- Verify Bootstrap 5 is loaded correctly

Advanced Customization
======================

Custom Mega Menu Layout
-----------------------

You can create unique layouts for each mega menu by adding different plugins and using Bootstrap classes.

Multiple Mega Menus
-------------------

Create multiple mega menus by repeating the process for different parent pages:

- Page "Products" → Reverse ID: ``products`` → Alias: ``mega-menu-products``
- Page "Services" → Reverse ID: ``services`` → Alias: ``mega-menu-services``
- Page "About" → Reverse ID: ``about`` → Alias: ``mega-menu-about``

Summary
=======

1. **Set Reverse ID** on parent page (e.g., ``about``) and enable it in navigation
2. **Visit the page** as a staff member – alias ``mega-menu-[reverse-id]`` is created automatically
3. **Edit the alias** and add plugins for your mega menu content
4. **Publish** the alias
5. **Done!** Your mega menu will appear in the navigation
