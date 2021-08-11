import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key"
    DEBUG = True
    CSRF_ENABLED = True

    CERT_FOLDER = get_env_variable("CERT_FOLDER")
    CA_FILE = f'{CERT_FOLDER}/{get_env_variable("ca")}'
    CERT_FILE = f'{CERT_FOLDER}/{get_env_variable("cert")}'
    KEY_FILE = f'{CERT_FOLDER}/{get_env_variable("key")}'

    KAFKA_BROKERS = get_env_variable("KAFKA_BROKERS")
    SECURITY_PROTOCOL = get_env_variable("SECURITY_PROTOCOL")

    ELASTIC_APM = {
        "SERVICE_NAME": get_env_variable("ELASTIC_SERVICE_NAME"),
        "SECRET_TOKEN": get_env_variable("ELASTIC_SECRET_TOKEN"),
        "SERVER_URL": get_env_variable("ELASTIC_SERVER_URL"),
        "DEBUG": True,
    }

    ll = get_env_variable("LOG_LEVEL")
    try:

        LOG_LEVEL = {0: logging.ERROR, 1: logging.WARN, 2: logging.INFO}[int(ll)]
    except KeyError:
        LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "prod-secret-key"


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    TESTING = False
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    # ELASTIC_APM['DEBUG']=True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "test-secret-key"
