from dotenv import load_dotenv
import os


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True


class Prod(Config):
    DEBUG = False


class Dev(Config):
    DEVELOPMENT = True
    DEBUG = True
