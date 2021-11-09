import yaml
import os
import logging
import logging.config
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app(config_name=None, config_path=None):
    app = Flask(__name__)
    # load config
    if not config_path:
        pwd = os.getcwd()
        config_path = os.path.join(pwd, 'config/config.yaml')
    if not config_name:
        config_name = 'DEVELOPMENT'
    conf = load_config(config_name, config_path)
    app.config.update(conf)

    # load logging
    if not os.path.exists(app.config['LOGGING_PATH']):
        os.mkdir(app.config['LOGGING_PATH'])
    with open(app.config['LOGGING_CONFIG_PATH'], 'r', encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f.read())
    logging.config.dictConfig(dict_conf)
    app.logger.info("Initializing...")
    return app


def load_config(config_name, config_path):
    if config_name and config_path:
        with open(config_path, 'r') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('can not find config name in yaml config file...')
    else:
        raise ValueError('please enter correct config name and config path...')

def make_limiter(app):
    limiter = Limiter(app,key_func=get_remote_address,default_limits=app.config['DEFAULT_RATE_LIMITS'])
    return limiter
