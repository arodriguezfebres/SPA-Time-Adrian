import os

# Unused, keeping in case Python packaging interferes with Pytest later on.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    ENV = "Development"


class DevConfig(Config):
    DEBUG = True
    ENV = "Development"


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    ENV = "Development"


class ProdConfig(Config):
    ENV = "Production"

