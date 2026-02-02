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
  tiptapAdmin: "backend/static/scss/tiptap-admin.scss",
  scss: "backend/static/scss/**/*.scss",
  outDir: "backend/static/css",
  tiptapOutDir: "backend/static/djangocms_text/css",
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
        outputStyle: isProd ? "compressed" : "expanded",
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
        outputStyle: "expanded",
      }).on("error", sass.logError)
    )
    .pipe(postcss([autoprefixer()]))
    .pipe(rename("tiptap.admin.css"))
    .pipe(gulp.dest(paths.tiptapOutDir));
}

function watchFiles() {
  gulp.watch(paths.scss, gulp.parallel(styles, tiptapAdminStyles));
}

const allStyles = gulp.parallel(styles, tiptapAdminStyles);

exports.styles = allStyles;
exports.watch = gulp.series(allStyles, watchFiles);
exports.build = gulp.series((done) => { process.env.NODE_ENV = "production"; done(); }, allStyles);
exports.default = exports.watch;
