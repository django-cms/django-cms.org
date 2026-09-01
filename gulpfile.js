const gulp = require("gulp");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const autoprefixer = require("autoprefixer");
const sourcemaps = require("gulp-sourcemaps");
const plumber = require("gulp-plumber");
const gulpIf = require("gulp-if");
const rename = require("gulp-rename");
const path = require("path");

const isProd = process.env.NODE_ENV === "production";

const paths = {
  entry: "backend/static/scss/main.scss",
  tiptapAdmin: "backend/static/scss/tiptap_admin.scss",
  scss: "backend/static/scss/**/*.scss",
  outDir: "backend/static/css",
  tiptapOutDir: "backend/static/djangocms_text/css",
  jsOutDir: "backend/static/js",
  // The .map goes with it: the bundle carries a //# sourceMappingURL comment,
  // and ManifestStaticFilesStorage resolves that reference at collectstatic
  // time — a missing map fails the build. It is only ever fetched when a
  // developer opens devtools.
  vendorJs: [
    "node_modules/bootstrap/dist/js/bootstrap.bundle.min.js",
    "node_modules/bootstrap/dist/js/bootstrap.bundle.min.js.map",
  ],
};

function styles() {
  return gulp
    .src(paths.entry, { allowEmpty: true })
    .pipe(gulpIf(!isProd, plumber()))
    .pipe(gulpIf(!isProd, sourcemaps.init()))
    .pipe(
      sass.sync({
        loadPaths: [
          path.resolve(__dirname, "backend/static/scss"), // falls du lokal imports hast
        ],
        quietDeps: true,
        silenceDeprecations: ["import", "global-builtin"],
        // "style", not "outputStyle": gulp-sass drives Dart Sass's modern API
        // (loadPaths/silenceDeprecations are modern-only options), which
        // silently ignores the legacy "outputStyle" key. Production CSS was
        // therefore shipping expanded — 377 KiB instead of 311 KiB.
        style: isProd ? "compressed" : "expanded",
      }).on("error", sass.logError)
    )
    .pipe(postcss([autoprefixer()]))
    .pipe(gulpIf(!isProd, sourcemaps.write(".")))
    .pipe(gulp.dest(paths.outDir));
}

function tiptapAdminStyles() {
  return gulp
    .src(paths.tiptapAdmin, { allowEmpty: true })
    .pipe(gulpIf(!isProd, plumber()))
    .pipe(
      sass.sync({
        loadPaths: [
          path.resolve(__dirname, "backend/static/scss"),
        ],
        quietDeps: true,
        silenceDeprecations: ["import", "global-builtin"],
        style: "expanded",
      }).on("error", sass.logError)
    )
    .pipe(postcss([autoprefixer()]))
    .pipe(rename("tiptap.admin.css"))
    .pipe(gulp.dest(paths.tiptapOutDir));
}

// Copy vendored browser JS straight from node_modules so the version served is
// the one pinned in package.json. base.html used to load the unminified
// bootstrap.bundle.js (208 KiB) on every page; the official minified bundle is
// 80 KiB.
function scripts() {
  return gulp.src(paths.vendorJs, { allowEmpty: true }).pipe(gulp.dest(paths.jsOutDir));
}

function watchFiles() {
  gulp.watch(paths.scss, gulp.parallel(styles, tiptapAdminStyles));
}

const allAssets = gulp.parallel(styles, tiptapAdminStyles, scripts);

exports.styles = allAssets;
exports.scripts = scripts;
exports.watch = gulp.series(allAssets, watchFiles);
exports.build = gulp.series((done) => { process.env.NODE_ENV = "production"; done(); }, allAssets);
exports.default = exports.watch;
