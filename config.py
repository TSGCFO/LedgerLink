class Config:
    SECRET_KEY = '2cfa48e50ed01e398251bd300540f905'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/billingapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/billingapp_test'

class ProductionConfig(Config):
    DEBUG = False
