===========================
Frontend Development Guide
===========================

This guide covers the frontend build setup for the django-cms.org project, including SCSS compilation and watch mode for local development.

Prerequisites
=============

- Node.js (version 20 or higher recommended)
- npm (comes with Node.js)

Setup
=====

Initial Installation
--------------------

Before you can use the build tools, install the required Node.js dependencies:

.. code-block:: bash

   npm install

This installs all dependencies defined in ``package.json``, including Gulp and SCSS compilation tools.

Available Commands
==================

Development Mode (with file watcher)
-------------------------------------

To start the SCSS file watcher for local development:

.. code-block:: bash

   npm run dev

Or simply:

.. code-block:: bash

   gulp

This command:

- Watches all SCSS files in ``backend/static/scss/`` for changes
- Automatically compiles SCSS to CSS when files are modified
- Generates source maps for easier debugging
- Outputs expanded (non-minified) CSS to ``backend/static/css/``

**Keep this running in a separate terminal while developing!**

Production Build
----------------

To build optimized CSS for production:

.. code-block:: bash

   npm run build

This command:

- Compiles SCSS to CSS once (no watching)
- Minifies/compresses the CSS output
- Does not generate source maps
- Sets ``NODE_ENV=production``

File Structure
==============

.. code-block:: text

   backend/static/
   ├── scss/
   │   ├── main.scss          # Main SCSS entry point
   │   ├── tiptap_admin.scss  # TipTap Admin Editor styles
   |   ├── theme/**.scss      # Bootstrap SCSS files
   │   └── **/*.scss          # All SCSS files (watched)
   ├── css/
   │   ├── main.css           # Compiled CSS output
   │   └── main.css.map       # Source map (dev mode only)
   └── djangocms_text/css/
       └── tiptap.admin.css   # Admin Editor styles (generated)

TipTap Admin Editor Styles
===========================

The project includes a separate SCSS file for styling the djangoCMS Text Editor (TipTap) in the admin interface. This ensures that colors and styles in the editor match your theme settings.

What It Does
------------

The ``tiptap_admin.scss`` file:

- Imports your theme variables (colors, fonts, etc.)
- Defines CSS classes for text and background colors used in the editor
- Compiles to ``backend/static/djangocms_text/css/tiptap.admin.css``
- Uses the same color values as your frontend theme
- Scopes all styles under ``.cms-admin`` to avoid conflicts

How It Works
------------

When you run ``npm run dev`` or ``npm run build``, two CSS files are compiled **in parallel**:

1. **main.css** - Your frontend styles
2. **tiptap.admin.css** - Admin editor styles

The build process automatically:

- Reads your theme colors from ``_variables.scss``
- Generates matching CSS for the editor
- Outputs to ``backend/static/djangocms_text/css/tiptap.admin.css``

Customizing Editor Colors
--------------------------

To add or modify colors in the editor:

1. **Update the SCSS file:**

   Edit ``backend/static/scss/tiptap_admin.scss`` and add your color class:

   .. code-block:: scss

      .cms-admin {
          .text-custom {
              color: $your-custom-color !important;
          }
      }

2. **Register in Django settings:**

   Add the color to ``TEXT_EDITOR_SETTINGS`` in ``backend/settings.py``:

   .. code-block:: python

      TEXT_EDITOR_SETTINGS = {
          "textColors": {
              "text-custom": {"name": "Custom Color"},
              # ... other colors
          },
      }

3. **Rebuild CSS:**

   The watcher will automatically rebuild, or run manually:

   .. code-block:: bash

      npx gulp styles

Why No Source Maps?
--------------------

The ``tiptap.admin.css`` file is intentionally compiled **without source maps** to keep the admin interface clean. The file is simple enough for debugging without source maps, and it reduces clutter in the admin CSS directory.

If you need source maps for debugging, you can modify ``gulpfile.js`` line 40-56 to add ``sourcemaps.init()`` and ``sourcemaps.write(".")``.

Local Development Workflow
===========================

Option 1: Docker + Local SCSS Watcher (Recommended)
----------------------------------------------------

Run Django in Docker and the SCSS watcher locally:

**Terminal 1 - Django (Docker):**

.. code-block:: bash

   docker compose up

**Terminal 2 - SCSS Watcher (Local):**

.. code-block:: bash

   npm run dev

This setup allows hot-reloading of styles without rebuilding Docker containers.

Option 2: Fully Local Development
----------------------------------

If running Django locally (without Docker):

**Terminal 1 - Django:**

.. code-block:: bash

   python manage.py runserver

**Terminal 2 - SCSS Watcher:**

.. code-block:: bash

   npm run dev

Production Deployment
=====================

In production (Docker), the SCSS is compiled during the Docker build process. See ``Dockerfile``:

.. code-block:: dockerfile

   FROM node:20-alpine AS build
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build  # <- Production build happens here

The compiled CSS is then copied into the final Python container, so no Node.js is needed at runtime.

Gulp Configuration
==================

The build process is configured in ``gulpfile.js``. Key features:

- **Environment detection**: Automatically detects ``NODE_ENV=production`` for optimized builds
- **Source maps**: Generated in development mode only
- **Autoprefixer**: Automatically adds vendor prefixes for browser compatibility
- **Error handling**: Uses ``gulp-plumber`` to prevent crashes on SCSS syntax errors (dev mode)

Troubleshooting
===============

``gulp: command not found``
---------------------------

You need to install dependencies first:

.. code-block:: bash

   npm install

Changes not reflected in browser
---------------------------------

1. Check that the watcher is running (``npm run dev``)
2. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for 404 errors on CSS files
4. Verify the compiled CSS exists in ``backend/static/css/``

Docker vs Local
---------------

- **Docker production build**: SCSS is compiled during ``docker compose build``
- **Local development**: You need to run ``npm install`` and ``npm run dev`` on your host machine
- ``node_modules/`` is in ``.gitignore`` (correct) - each environment needs its own installation

TipTap Admin CSS not updating
------------------------------

If changes to ``tiptap_admin.scss`` aren't reflected in the admin:

1. Verify the file is being compiled:

   .. code-block:: bash

      ls -la backend/static/djangocms_text/css/tiptap.admin.css

2. Check that the file is not in ``.gitignore`` (it should be)
3. Rebuild manually:

   .. code-block:: bash

      npx gulp styles

4. Restart Django (``python manage.py runserver`` or ``docker compose restart``)
5. Hard refresh browser in admin (Ctrl+F5)

Adding New SCSS Files
======================

1. Create your SCSS file in ``backend/static/scss/``
2. Import it in ``main.scss``:

   .. code-block:: scss

      @import 'components/your-new-file';

3. The watcher (if running) will automatically detect and compile it

Additional Resources
====================

- `Gulp Documentation <https://gulpjs.com/>`_
- `Sass Documentation <https://sass-lang.com/>`_
- `Autoprefixer <https://github.com/postcss/autoprefixer>`_
