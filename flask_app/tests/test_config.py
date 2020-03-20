from flask import Flask

from flask_app import run

test_app = Flask(__name__)


def test_dev_config():
    run.set_config(test_app, 'config.DevConfig')
    assert test_app.config['ENV'] == 'Development'
    assert test_app.config['DEBUG']


def test_test_config():
    run.set_config(test_app, 'config.TestConfig')
    assert test_app.config['ENV'] == 'Development'
    assert test_app.config['TESTING']
    assert test_app.config['DEBUG']


def test_production_config():
    run.set_config(test_app, 'config.ProdConfig')
    assert test_app.config['ENV'] == 'Production'
    assert not test_app.config['DEBUG']
