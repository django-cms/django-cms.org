django-cms.org
==============

This repository contains the source code for the official `django-cms.org` website.

Overview
--------

The site is built using the `django-cms-quickstarter` project as its foundation, providing a modern and maintainable setup for running the django CMS-powered website.

Features
--------

- Powered by [django CMS](https://www.django-cms.org/)
- Based on the [django-cms-quickstarter](https://github.com/django-cms/django-cms-quickstarter) template
- Modular and extensible project structure
- Easily customizable for content and design
- Custom `cms_theme` app containing website design files and custom djangocms-frontend components

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

You need to have Docker installed on your system to run this project.

- `Install Docker <https://docs.docker.com/engine/install/>`_ here
- If you have not used Docker in the past, please read this `introduction on Docker <https://docs.docker.com/get-started/>`_

Local Development Setup
~~~~~~~~~~~~~~~~~~~~~~~

1. Clone this repository:

  .. code-block:: bash

    git clone https://github.com/django-cms/django-cms.org.git
    cd django-cms.org

2. Build and start the project using Docker Compose:

  .. code-block:: bash

    docker compose build web
    docker compose up -d database_default
    docker compose run web python manage.py migrate
    docker compose run web python manage.py createsuperuser
    docker compose up -d

3. Open your browser and navigate to:

   http://django-cms.org.127.0.0.1.nip.io:8000 (or just http://127.0.0.1:8000)


Contributing
------------

Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

License
-------

This project is licensed under the terms of the MIT License.

Frontend Development
--------------------

This project uses Bootstrap SCSS and Gulp for frontend asset compilation. For detailed information about the frontend development workflow, including:

- SCSS architecture and file structure
- Bootstrap customization
- Gulp task configuration
- Development and production builds
- File watching

Please refer to the comprehensive guide:

📖 **[Frontend Development Guide](docs/frontend_development_guide.rst)**

Quick Start
~~~~~~~~~~~

Install dependencies and start development:

.. code-block:: bash

   npm install
   npm run dev

Build for production:

.. code-block:: bash

   npm run build

Mega Menu Setup
---------------

This project includes a powerful mega menu system that allows you to create rich, customizable navigation dropdowns using django CMS pages and djangocms-alias. For detailed information about:

- Setting up parent pages with reverse IDs
- Creating mega menu aliases
- Customizing mega menu layouts
- Styling and responsive behavior
- Troubleshooting

Please refer to the comprehensive guide:

📖 **[Mega Menu Setup Guide](docs/mega-menu-setup.rst)**

Quick Overview
~~~~~~~~~~~~~~

1. Set a **Reverse ID** on your parent page (e.g., ``about``)
2. Create an **Alias** named ``mega-menu-[reverse-id]`` (e.g., ``mega-menu-about``)
3. Add content plugins to your alias
4. Publish and enjoy your mega menu!

