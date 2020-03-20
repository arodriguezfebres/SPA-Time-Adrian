import sys

import requests
from flask import Flask, request, url_for

from api import api_bp

my_app = Flask(__name__)


@my_app.route('/')
def index():
    time_url = request.base_url + url_for('api.time')
    response = requests.get(time_url).json()
    if response and response[0].get('curr_time'):
        return f"The current date and time is: {response[0].get('curr_time')}."
    return 'Date and time retrieval failed.'


def set_config(in_app, filename):
    in_app.config.from_object(filename)


def create_app(in_config):
    set_config(my_app, in_config)

    # API
    my_app.register_blueprint(api_bp, url_prefix='/api')

    return my_app


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = 'config.DevConfig'

    my_app = create_app(config)
    my_app.run()
