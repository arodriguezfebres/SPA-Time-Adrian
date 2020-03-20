from datetime import datetime

from flask import jsonify
from flask_restful import Resource


def time_as_formatted_str():
    dt_now = datetime.now()
    dt_now_formatted = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return dt_now_formatted


class Time(Resource):
    def get(self):
        status_code = 200
        try:
            curr_time = time_as_formatted_str()
            return jsonify({'curr_time': curr_time}, status_code)
        except Exception as exception:  # General exception catch, suboptimal.
            status_code = 418
            return jsonify({'curr_time': 'ERROR - Unknown.'}, status_code, {'Content-Type': 'application/json'})
