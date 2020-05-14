class Configuration(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    MSEARCH_ENABLE = True
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://name_base:password@localhost/name_base'
    SQLALCHEMY_POOL_PING = True
    SQLALCHEMY_POOL_RECYCLE = 60
    SECRET_KEY = 'secret_key'