# Django settings for lasso project.
import os.path, sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_IN_TERMINAL = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'lasso'             # Or path to database file if using sqlite3.
DATABASE_USER = 'lasso'             # Not used with sqlite3.
DATABASE_PASSWORD = 'lasso'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://localhost:8000/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'SALTGURKASALTGURKASALTGURKASALTGURKASALTGURKASALTG'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "lasso.context_processors.settings_processor"
    ]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'excware.ExcWare',
)

ROOT_URLCONF = 'lasso.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'lasso.lasso_auth',
    'lasso.lasso_global',
    'lasso.lasso_warehouse',
    'lasso.lasso_customer',
    'lasso.lasso_warehandling',
    'lasso.lasso_labelprinting',
    'lasso.lasso_import',
    'lasso.i18next',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'rosetta',
)

LASSO_LABELPRINTING_PRINTER = ("127.0.0.1", 9100)

LASSO_DEFAULT_PLACE_OF_DEPARTURE="Pratteln"

USE_L10N=True

CONTENTTYPE_NO_TRAVERSE_PROXY=True

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
for name in ['/etc/lasso.py', os.path.join(os.path.dirname(__file__), "local_settings.py")]:
    if os.path.exists(name):
        sys.stderr.write("Loading local settings from " + name + "\n")
        with open(name) as f:
            exec f
        break
