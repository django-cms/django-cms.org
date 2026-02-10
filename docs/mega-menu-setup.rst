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

1. Create Parent Page with Reverse ID
--------------------------------------

To enable a dropdown menu for a navigation item, you need to:

1. **Create or edit a page** that should have the dropdown menu
2. **Go to Advanced Settings** of the page
3. **Set a Reverse ID** - this is crucial for linking the page to its mega menu alias

**Example:**

- Page Title: "About Django CMS"
- Reverse ID: ``about`` (use lowercase, no spaces)

.. note::
   The reverse ID must be unique across your site. It acts as an identifier to connect the page with its mega menu content.

2. Create the Mega Menu Alias
------------------------------

Now create an alias that will contain your mega menu content:

1. **Go to Aliases** in your django CMS admin
2. **Click "Add Alias"**
3. **Name your alias** using the format: ``mega-menu-[reverse-id]``

   - For the example above: ``mega-menu-about``

4. **Add plugins** to the alias placeholder to build your mega menu content

   - You can use any plugins: Text, Images, Links, Cards, etc.
   - Use Bootstrap grid classes for layout (row, col-lg-4, etc.)

**Naming Convention:**

.. code-block:: text

   mega-menu-[reverse-id]

- If reverse ID is ``about``, alias name is ``mega-menu-about``
- If reverse ID is ``services``, alias name is ``mega-menu-services``

3. How It Works
---------------

The system automatically connects pages to their mega menus:

1. **Navigation rendering** checks if a page has child pages
2. **If the page has children**, it renders a dropdown toggle
3. **The template looks for** a reverse ID on the page
4. **If a reverse ID exists**, it loads the alias: ``mega-menu-[reverse-id]``
5. **The alias content** is rendered inside the dropdown menu

4. Template Structure
---------------------

The menu template (``templates/menu/menu.html``) handles this logic:

.. code-block:: django

   {% if child.children %}
     <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown">
       {{ child.get_menu_title }}
     </a>

     <div class="dropdown-menu">
       {% if child.attr.reverse_id %}
         {# Load mega menu alias #}
         {% static_alias "mega-menu-"|add:child.attr.reverse_id %}
       {% else %}
         {# Fallback: render simple dropdown #}
         {% include "menu/dropdown.html" with parent=child %}
       {% endif %}
     </div>
   {% endif %}

Example: Creating an "About" Mega Menu
=======================================

Page Setup
----------

1. Create page titled "About Django CMS"
2. Add child pages (Who we serve, Our Story, etc.)
3. Set Reverse ID: ``about``
4. Publish the page

Alias Setup
-----------

1. Create alias named: ``mega-menu-about``
2. Add content structure:

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

3. Publish the alias

Result
------

The "About Django CMS" menu item will now show a rich mega menu with your custom content when hovered or clicked.

Fallback Behavior
=================

If you don't create a mega menu alias, the system automatically falls back to rendering a simple dropdown menu with links to the child pages.

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
2. **Use Bootstrap grid**: Organize mega menu content with Bootstrap's grid system
3. **Test responsive**: Ensure your mega menu works on all screen sizes
4. **Use preview**: The alias preview shows how your mega menu will look
5. **Reuse aliases**: You can use the same alias for multiple pages if needed

Troubleshooting
===============

Mega menu not showing
---------------------

- Check that the page has child pages
- Verify the reverse ID is set correctly
- Ensure the alias name matches: ``mega-menu-[reverse-id]``
- Check that the alias is published

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

You can create unique layouts for each mega menu by adding different plugins and using Bootstrap classes:

.. code-block:: django

   {# Example: Two-column mega menu #}
   <div class="row">
     <div class="col-lg-6">
       {# Left column content #}
     </div>
     <div class="col-lg-6">
       {# Right column content #}
     </div>
   </div>

Multiple Mega Menus
-------------------

Create multiple mega menus by repeating the process for different parent pages:

- Page "Products" → Reverse ID: ``products`` → Alias: ``mega-menu-products``
- Page "Services" → Reverse ID: ``services`` → Alias: ``mega-menu-services``
- Page "About" → Reverse ID: ``about`` → Alias: ``mega-menu-about``

Summary
=======

1. **Set Reverse ID** on parent page (e.g., ``about``)
2. **Create Alias** named ``mega-menu-[reverse-id]`` (e.g., ``mega-menu-about``)
3. **Add Content** to alias using plugins
4. **Publish** both page and alias
5. **Done!** Your mega menu will appear in the navigation
