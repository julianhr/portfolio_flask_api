import os


class Config:
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']


class DevelopmentConfig(Config):
    DEBUG = True
    SENTRY_SDK_DSN = os.environ['SENTRY_SDK_DSN']


class TestingConfig(Config):
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    SENTRY_SDK_DSN = os.environ['SENTRY_SDK_DSN']


app_config = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    testing=TestingConfig,
)
