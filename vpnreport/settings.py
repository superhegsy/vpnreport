"""
Django settings for vpnreport project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================
# SECURITY
# ===============================

SECRET_KEY = 'django-insecure-gh1$yurgv+5k(qz$b1la%k6i1%aqi3f)8fzp#s&o+9)=lt_kd&'

DEBUG = True

ALLOWED_HOSTS = [
    "10.101.95.19",
    "vpn-report",
    "localhost",
    "127.0.0.1",
]


# ===============================
# APPLICATIONS
# ===============================

INSTALLED_APPS = [

    # DJANGO CORE
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # PROJECT APPS
    'app',
    'vpn',

]


# ===============================
# MIDDLEWARE
# ===============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ===============================
# URLS
# ===============================

ROOT_URLCONF = 'vpnreport.urls'


# ===============================
# TEMPLATES
# ===============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ===============================
# WSGI
# ===============================

WSGI_APPLICATION = 'vpnreport.wsgi.application'


# ===============================
# DATABASE
# ===============================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ===============================
# PASSWORD VALIDATION
# ===============================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ===============================
# INTERNATIONAL
# ===============================

LANGUAGE_CODE = 'hu'

TIME_ZONE = 'Europe/Budapest'

USE_I18N = True

USE_TZ = True


# ===============================
# STATIC FILES
# ===============================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ===============================
# LOGIN SETTINGS
# ===============================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# ===============================
# DEFAULT FIELD TYPE
# ===============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
