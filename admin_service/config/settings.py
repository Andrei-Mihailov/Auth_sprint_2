
from pathlib import Path
import os
from dotenv import load_dotenv
from split_settings.tools import include


load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False) == 'True'


include(
    'components/database.py',
    'components/installed_apps.py',
    'components/middlewares.py',
    'components/templates.py',
    'components/pass_validators.py'
)

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').replace(
    '[', '').replace(']', '').replace('\'', '').split(',')


ROOT_URLCONF = 'config.urls'


WSGI_APPLICATION = 'config.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/movies/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'movies')

AUTH_USER_MODEL = "users.User"

AUTH_API_LOGIN_URL = os.environ.get('AUTH_API_LOGIN_URL')
