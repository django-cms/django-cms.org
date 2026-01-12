# Frontend Development Guide

This guide covers the frontend build setup for the django-cms.org project, including SCSS compilation and watch mode for local development.

## Prerequisites

- Node.js (version 20 or higher recommended)
- npm (comes with Node.js)

## Setup

### Initial Installation

Before you can use the build tools, install the required Node.js dependencies:

```bash
npm install
```

This installs all dependencies defined in `package.json`, including Gulp and SCSS compilation tools.

## Available Commands

### Development Mode (with file watcher)

To start the SCSS file watcher for local development:

```bash
npm run dev
```

Or simply:

```bash
gulp
```

This command:
- Watches all SCSS files in `backend/static/scss/` for changes
- Automatically compiles SCSS to CSS when files are modified
- Generates source maps for easier debugging
- Outputs expanded (non-minified) CSS to `backend/static/css/`

**Keep this running in a separate terminal while developing!**

### Production Build

To build optimized CSS for production:

```bash
npm run build
```

This command:
- Compiles SCSS to CSS once (no watching)
- Minifies/compresses the CSS output
- Does not generate source maps
- Sets `NODE_ENV=production`

## File Structure

```
backend/static/
├── scss/
│   ├── main.scss          # Main SCSS entry point
│   └── **/*.scss          # All SCSS files (watched)
└── css/
    ├── main.css           # Compiled CSS output
    └── main.css.map       # Source map (dev mode only)
```

## Local Development Workflow

### Option 1: Docker + Local SCSS Watcher (Recommended)

Run Django in Docker and the SCSS watcher locally:

**Terminal 1 - Django (Docker):**
```bash
docker compose up
```

**Terminal 2 - SCSS Watcher (Local):**
```bash
npm run dev
```

This setup allows hot-reloading of styles without rebuilding Docker containers.

### Option 2: Fully Local Development

If running Django locally (without Docker):

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - SCSS Watcher:**
```bash
npm run dev
```

## Production Deployment

In production (Docker), the SCSS is compiled during the Docker build process. See `Dockerfile`:

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build  # <- Production build happens here
```

The compiled CSS is then copied into the final Python container, so no Node.js is needed at runtime.

## Gulp Configuration

The build process is configured in `gulpfile.js`. Key features:

- **Environment detection**: Automatically detects `NODE_ENV=production` for optimized builds
- **Source maps**: Generated in development mode only
- **Autoprefixer**: Automatically adds vendor prefixes for browser compatibility
- **Error handling**: Uses `gulp-plumber` to prevent crashes on SCSS syntax errors (dev mode)

## Troubleshooting

### `gulp: command not found`

You need to install dependencies first:
```bash
npm install
```

### Changes not reflected in browser

1. Check that the watcher is running (`npm run dev`)
2. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for 404 errors on CSS files
4. Verify the compiled CSS exists in `backend/static/css/`

### Docker vs Local

- **Docker production build**: SCSS is compiled during `docker compose build`
- **Local development**: You need to run `npm install` and `npm run dev` on your host machine
- `node_modules/` is in `.gitignore` (correct) - each environment needs its own installation

## Adding New SCSS Files

1. Create your SCSS file in `backend/static/scss/`
2. Import it in `main.scss`:
   ```scss
   @import 'components/your-new-file';
   ```
3. The watcher (if running) will automatically detect and compile it

## Additional Resources

- [Gulp Documentation](https://gulpjs.com/)
- [Sass Documentation](https://sass-lang.com/)
- [Autoprefixer](https://github.com/postcss/autoprefixer)
