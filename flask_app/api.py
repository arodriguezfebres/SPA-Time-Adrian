from flask import Blueprint
from flask_restful import Api

from fetch_time import Time

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
api.add_resource(Time, '/time')
