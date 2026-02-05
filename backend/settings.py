import os
from copy import deepcopy
from pathlib import Path

import dj_database_url
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy as _
from django_storage_url import dsn_configured_storage_class

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "<a string of random characters>")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG") == "True"

ALLOWED_HOSTS = [
    os.environ.get("DOMAIN"),
]
if DEBUG:
    ALLOWED_HOSTS = [
        "*",
    ]

# Redirect to HTTPS by default, unless explicitly disabled
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT") != "False"

X_FRAME_OPTIONS = "SAMEORIGIN"


# Application definition

INSTALLED_APPS = [
    "backend",
    # optional, but used in most projects
    "djangocms_simple_admin_style",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.redirects",
    "whitenoise.runserver_nostatic",  # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # key django CMS modules
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    # Django Filer - optional, but used in most projects
    "filer",
    "easy_thumbnails",
    # the default publishing implementation - optional, but used in most projects
    "djangocms_versioning",
    # the default alias content - optional, but used in most projects
    "djangocms_alias",
    "parler",
    # the default text editor - optional, but used in most projects
    "djangocms_text",
    # optional django CMS frontend modules
    "djangocms_frontend",
    "djangocms_frontend.contrib.accordion",
    "djangocms_frontend.contrib.alert",
    "djangocms_frontend.contrib.badge",
    "djangocms_frontend.contrib.card",
    "djangocms_frontend.contrib.carousel",
    "djangocms_frontend.contrib.collapse",
    "djangocms_frontend.contrib.content",
    "djangocms_frontend.contrib.grid",
    "djangocms_frontend.contrib.icon",
    "djangocms_frontend.contrib.image",
    "djangocms_frontend.contrib.jumbotron",
    "djangocms_frontend.contrib.link",
    "djangocms_frontend.contrib.listgroup",
    "djangocms_frontend.contrib.media",
    "djangocms_frontend.contrib.tabs",
    "djangocms_frontend.contrib.utilities",
    "djangocms_link",
    # Specific designs for this site
    "cms_theme",
    "djangocms_video",
    "djangocms_ecosystem",
    # djangocms-stories-related stuff
    "djangocms_stories",
    "taggit",
    "taggit_autosuggest",
    "meta",
    "sortedm2m",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.template.context_processors.i18n",
                "cms.context_processors.cms_settings",
                "sekizai.context_processors.sekizai",
            ],
        },
    },
]

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    #'easy_thumbnails.processors.scale_and_crop',
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

CMS_TEMPLATES = [
    # optional templates that extend base.html, to be used with Bootstrap 5
    ("cms_theme/base.html", "Default"),
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# Configure database using DATABASE_URL; fall back to sqlite in memory when no
# environment variable is available, e.g. during Docker build
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://:memory:")
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

if not DEBUG:
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_collected")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
# DEFAULT_FILE_STORAGE is configured using DEFAULT_STORAGE_DSN

# read the setting value from the environment variable
DEFAULT_STORAGE_DSN = os.environ.get("DEFAULT_STORAGE_DSN")

# dsn_configured_storage_class() requires the name of the setting
DefaultStorageClass = dsn_configured_storage_class("DEFAULT_STORAGE_DSN")

# Django's DEFAULT_FILE_STORAGE requires the class name
DEFAULT_FILE_STORAGE = "backend.settings.DefaultStorageClass"

# only required for local file storage and serving, in development
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join("/data/media/")


SITE_ID = 1

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TEXT_INLINE_EDITING = True
CMS_CONFIRM_VERSION4 = True
DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True


# Activate webp support
THUMBNAIL_PRESERVE_EXTENSIONS = ("webp",)
THUMBNAIL_TRANSPARENCY_EXTENSION = "webp"

# For development: django-debug-toolbar
if DEBUG or True:
    INSTALLED_APPS += (  # NoQA F405
        "debug_toolbar",
    )
    MIDDLEWARE.insert(  # NoQA F405
        0,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = [
        "127.0.0.1",
    ]
    ADMINS = [
        ("Fabian", "fsbraun@gmx.de"),
    ]
    LOGGING = deepcopy(DEFAULT_LOGGING)
    LOGGING["handlers"]["mail_admins"]["include_html"] = True
    LOGGING["handlers"]["mail_admins"]["filters"] = []

# Design settings
STORIES_PLUGIN_TEMPLATE_FOLDERS = (
    ("plugins", _("Default")),
    ("cards", _("Cards")),
)

# djangocms-frontend settings
DJANGOCMS_FRONTEND_ADMIN_CSS = {
    "all": ("css/main.css",),
}

DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES = (
    ("primary", _("Primary")),
    ("secondary", _("Secondary")),
    ("success", _("Success")),
    ("danger", _("Danger")),
    ("warning", _("Warning")),
    ("info", _("Info")),
    ("light", _("Light")),
    ("dark", _("Dark")),
    ("second-primary", _("Dark Green")),
    ("white", _("White")),
    ("platinum", _("Platinum")),
    ("gold", _("Gold")),
    ("silver", _("Silver")),
    ("bronze", _("Bronze")),
)

DJANGOCMS_FRONTEND_SPACER_SIZES = (
    ("0", "* 0"),
    ("1", "* .25"),
    ("2", "* .5"),
    ("3", "* 1"),
    ("4", "* 1.5"),
    ("5", "* 3"),
    ("6", "* 4"),
    ("7", "* 5"),
    ("8", "* 6"),
    ("9", "* 7"),
    ("10", "* 8"),
)

# djangocms-text settings
TEXT_EDITOR_SETTINGS = {
    "inlineStyles": [
        {
            "name": "Small",
            "element": "small",
        },
        {
            "name": "Kbd",
            "element": "kbd",
        },
        {
            "name": "Kbd",
            "element": "kbd",
        },
        {
            "name": "Var",
            "element": "var",
        },
        {
            "name": "Samp",
            "element": "samp",
        },
        {
            "name": "Overline",
            "element": "span",
            "attributes": {
                "class": "overline",
            },
        },
        {
            "name": "Lead",
            "element": "span",
            "attributes": {
                "class": "lead",
            },
        },
        {
            "name": "Text XS",
            "element": "span",
            "attributes": {
                "class": "fs-6",
            },
        },
        {
            "name": "Text SM",
            "element": "span",
            "attributes": {
                "class": "fs-5",
            },
        },
        {
            "name": "Text LG",
            "element": "span",
            "attributes": {
                "class": "fs-4",
            },
        },
    ],
    "textColors": {
        "text-primary": {"name": "Primary"},
        "text-secondary": {"name": "Secondary"},
        "text-success": {"name": "Success"},
        "text-warning": {"name": "Warning"},
        "text-info": {"name": "Info"},
        "text-danger": {"name": "Danger"},
        "text-body": {"name": "Body"},
        "text-light": {"name": "Light"},
        "text-dark": {"name": "Dark"},
        "text-muted": {"name": "Muted"},
        "text-white": {"name": "White"},
    },
}
