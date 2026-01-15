const gulp = require("gulp");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const autoprefixer = require("autoprefixer");
const sourcemaps = require("gulp-sourcemaps");
const plumber = require("gulp-plumber");
const gulpIf = require("gulp-if");
const path = require("path");

const isProd = process.env.NODE_ENV === "production";

const paths = {
  entry: "backend/static/scss/main.scss",
  scss: "backend/static/scss/**/*.scss",
  outDir: "backend/static/css",
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

function watchFiles() {
  gulp.watch(paths.scss, styles);
}

exports.styles = styles;
exports.watch = gulp.series(styles, watchFiles);
exports.build = gulp.series((done) => { process.env.NODE_ENV = "production"; done(); }, styles);
exports.default = exports.watch;
