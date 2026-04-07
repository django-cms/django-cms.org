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
    "djangocms_markdown",
    # Specific designs for this site
    "cms_theme",
    "djangocms_video",
    "djangocms_ecosystem",
    # optional django CMS frontend modules
    "djangocms_frontend",
    "djangocms_frontend.contrib.alert",
    "djangocms_frontend.contrib.card",
    "djangocms_frontend.contrib.content",
    "djangocms_frontend.contrib.grid",
    "djangocms_frontend.contrib.icon",
    "djangocms_frontend.contrib.image",
    "djangocms_frontend.contrib.link",
    "djangocms_frontend.contrib.listgroup",
    "djangocms_frontend.contrib.media",
    "djangocms_link",
    # djangocms-stories-related stuff
    "djangocms_stories",
    "authors",
    "taggit",
    "taggit_autosuggest",
    "meta",
    "sortedm2m",
    "djangocms_file",
    "djangocms_form_builder",

    "djangocms4_utilities",
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

CMS_DEFAULT_IN_NAVIGATION = False

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

CMS_LANGUAGES = {
    1: [
        {
            "code": "en",
            "name": "English",
        },
    ],
    "default": {
        "fallbacks": ["en"],
        "redirect_on_fallback": False,
        "public": True,
        "hide_untranslated": False,
    },
}

PARLER_LANGUAGES = {
    1: (
        {
            "code": "en",
        },
    ),
    "default": {
        "fallbacks": [
            "en",
        ],
    },
}

PARLER_DEFAULT_LANGUAGE_CODE = "en"
PARLER_ENABLE_CACHING = False

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_collected")

# Media files
# DEFAULT_FILE_STORAGE is configured using DEFAULT_STORAGE_DSN

# read the setting value from the environment variable
DEFAULT_STORAGE_DSN = os.environ.get("DEFAULT_STORAGE_DSN")

# only required for local file storage and serving, in development
MEDIA_URL = "/media/"
if DEFAULT_STORAGE_DSN:
    DefaultStorageClass = dsn_configured_storage_class("DEFAULT_STORAGE_DSN")
    STORAGES = {
        "default": {"BACKEND": "backend.settings.DefaultStorageClass"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    # Thumbnails + filer sollen den default storage nutzen (also S3)
    THUMBNAIL_DEFAULT_STORAGE = "default"
    FILER_STORAGES = {
        "public": {"main": {"BACKEND": "django.core.files.storage.DefaultStorage"}},
        "private": {"main": {"BACKEND": "django.core.files.storage.DefaultStorage"}},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")


SITE_ID = 1

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TEXT_INLINE_EDITING = True
CMS_CONFIRM_VERSION4 = True
DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True


# Activate webp support
THUMBNAIL_PRESERVE_EXTENSIONS = ("webp",)
THUMBNAIL_TRANSPARENCY_EXTENSION = "webp"

# For development: django-debug-toolbar
if DEBUG:
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
    ("cards", _("Cards Image on Top")),
    ("cards_author", _("Cards with Author")),
    ("events", _("Events")),
)

# django-meta settings
META_SITE_PROTOCOL = os.environ.get("META_SITE_PROTOCOL", "https")
META_SITE_DOMAIN = os.environ.get("DOMAIN", "localhost:8000")
META_USE_SITES = True

# djangocms-stories settings
STORIES_URLCONF = "backend.blog_urls"
# djangocms-stories settings
STORIES_PAGINATION = 25
STORIES_LATEST_ENTRIES = 5
STORIES_ENABLE_TAGS = True
STORIES_TEMPLATE_CHOICES = (("blog/post_list.html", _("Default")),)


# djangocms-frontend settings
DJANGOCMS_FRONTEND_SHOW_ADVANCED_SETTINGS = False
DJANGOCMS_FRONTEND_COMPONENT_FIELDS = {
    "cms_theme": "cms_theme.fields.ColorChoiceField",
}

DJANGOCMS_FRONTEND_ADMIN_CSS = {
    "all": ("css/admin_colors.css",),
}

DJANGOCMS_FRONTEND_ICON_LIBRARIES_SHOWN = (
    "font-awesome",
    "font-awesome-light",
    "font-awesome-thin",
    "bootstrap-icons",
    "material-icons-filled",
    "material-icons-outlined",
    "material-icons-round",
    "material-icons-sharp",
    "material-icons-two-tone",
    "fomantic-ui",
    "foundation-icons",
    "elegant-icons",
    "feather-icons",
    "open-iconic",
    "tabler-icons",
    "weather-icons",
)

DJANGOCMS_FRONTEND_ICONS_LIBRARIES_SHOWN = DJANGOCMS_FRONTEND_ICON_LIBRARIES_SHOWN

_DJANGOCMS_FRONTEND_ICON_CDN = {
    "bootstrap-icons": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.4/font/bootstrap-icons.css",
    "font-awesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    "material-icons-filled": "https://fonts.googleapis.com/css2?family=Material+Icons",
    "material-icons-outlined": "https://fonts.googleapis.com/css2?family=Material+Icons+Outlined",
    "material-icons-round": "https://fonts.googleapis.com/css2?family=Material+Icons+Round",
    "material-icons-sharp": "https://fonts.googleapis.com/css2?family=Material+Icons+Sharp",
    "material-icons-two-tone": "https://fonts.googleapis.com/css2?family=Material+Icons+Two+Tone",
    "fomantic-ui": "fomantic-ui-icons.css",
}

DJANGOCMS_FRONTEND_ICON_LIBRARIES = {
    "font-awesome-light": ("font-awesome-light.min.json", "font-awesome-light.css"),
    "font-awesome-thin": ("font-awesome-thin.min.json", "font-awesome-thin.css"),
}

DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES = (
    ("primary", _("Primary")),
    ("secondary", _("Secondary")),
    ("light", _("Light")),
    ("dark", _("Dark")),
    ("black", _("Black")),
    ("second-primary", _("Dark Green")),
    ("white", _("White")),
    ("platinum", _("Platinum")),
    ("gold", _("Gold")),
    ("silver", _("Silver")),
    ("bronze", _("Bronze")),
)

DJANGO_FORM_BUILDER_COLOR_STYLE_CHOICES = (
    ("primary", _("Primary")),
    ("secondary", _("Secondary")),
    ("second-primary", _("Dark Green")),
)
DJANGOCMS_FORM_BUILDER_COLOR_STYLE_CHOICES = DJANGO_FORM_BUILDER_COLOR_STYLE_CHOICES

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

# Hero clip path shapes available in the Hero plugin.
# Each entry is a 3-tuple: (id, label, config)
# config is a dict with keys: view_width, view_height, path
# Use None as config to represent the "no clip path" choice.
CMS_HERO_CLIP_PATHS = [
    ("none", _("None"), None),
    (
        "staggered-boxes",
        _("Staggered Boxes"),
        {
            "view_width": 630,
            "view_height": 522,
            "path": (
                "M118.033 0.5H525.699C533.956 0.5 540.649 7.19354 540.649 15.4502V302.37H614.551"
                "C622.807 302.37 629.501 309.064 629.501 317.32V505.703L629.496 506.089"
                "C629.291 514.167 622.678 520.653 614.551 520.653H423.32C415.064 520.653 408.37 513.96"
                " 408.37 505.703V448.033H118.033C109.777 448.033 103.084 441.34 103.084 433.083V294.251"
                "H15.4502C7.19361 294.251 0.500104 287.557 0.5 279.301V90.918C0.5 82.6613 7.19354"
                " 75.9678 15.4502 75.9678H103.084V15.4502C103.084 7.19362 109.777 0.500178 118.033 0.5Z"
            ),
        },
    ),
    (
        "offset-panel",
        _("Offset Panel"),
        {
            "view_width": 342,
            "view_height": 427,
            "path": (
                "M20.2031 0.5H264.91C275.681 0.500093 284.412 9.23139 284.412 20.002V155.768H321.999"
                "C332.769 155.768 341.501 164.499 341.501 175.27V357.108L341.494 357.611"
                "C341.227 368.149 332.601 376.61 321.999 376.61H49.6807V406.998C49.6807 417.769"
                " 40.9493 426.5 30.1787 426.5H-68.1514C-78.9219 426.5 -87.6533 417.769"
                " -87.6533 406.998V305.253L-87.6465 304.75C-87.3838 294.379 -79.0252 286.02"
                " -68.6543 285.758L-68.1514 285.751H-18.041V250.726H-178.998C-189.769 250.726"
                " -198.5 241.994 -198.5 231.224V57.2148C-198.5 46.4442 -189.769 37.7129"
                " -178.998 37.7129H0.701172V20.002C0.701172 9.39947 9.162 0.773604 19.7002 0.506836"
                "L20.2031 0.5Z"
            ),
        },
    ),
    (
        "side-panel",
        _("Side Panel"),
        {
            "view_width": 750,
            "view_height": 672,
            "path": (
                "M268 0.5H730C740.77 0.5 749.5 9.23045 749.5 20V652L749.493 652.503"
                "C749.226 663.04 740.601 671.5 730 671.5H268C257.23 671.5 248.5 662.77 248.5 652"
                "V594.5H20C9.23045 594.5 0.5 585.77 0.5 575V167L0.506836 166.497"
                "C0.773605 155.96 9.3986 147.5 20 147.5H248.5V20C248.5 9.3986 256.96 0.773603"
                " 267.497 0.506836L268 0.5Z"
            ),
        },
    ),
]

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
    "blockStyles": [
        {
            "name": "Blockquote",
            "element": "blockquote",
            "attributes": {
                "class": "blockquote",
            },
        },
        {
            "name": "Lead",
            "element": "p",
            "attributes": {
                "class": "lead",
            },
        },
    ],
    "textColors": {
        "text-primary": {"name": "Primary"},
        "text-secondary": {"name": "Secondary"},
        "text-body": {"name": "Body"},
        "text-light": {"name": "Light"},
        "text-dark": {"name": "Dark"},
        "text-muted": {"name": "Muted"},
        "text-white": {"name": "White"},
    },
}

# djangocms-file settings
DJANGOCMS_FILE_TEMPLATES = [
    ("secondary", _("Secondary file link")),
    ("primary", _("Primary file link")),
]

# djangocms-picture settings
DJANGOCMS_PICTURE_TEMPLATES = [
    ("default", _("Default")),
    ("decorated", _("Decorated")),
    ("clipped_0", _("Group clipped")),
    ("clipped_1", _("Slingle person clipped with panel")),
    ("clipped_2", _("Single person clipped")),
]

# Use image as a component in templates
CMS_COMPONENT_PLUGINS = [
    "ImagePlugin",
]

CMS_PLACEHOLDER_CONF = {
    "content": {
        "excluded_plugins": [
            "FooterPlugin",
            "CardPlugin",
            "CardLayoutPlugin",
            "GridRowPlugin",
            "GridContainerPlugin",
            "FigurePlugin",
        ]
    }
}

if not DEBUG:
    import sentry_sdk
    sentry_sdk.init(
        dsn="https://f8c524803172e25fffe7e04be0e9fdc5@o4511032249155584.ingest.de.sentry.io/4511032253415504",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )