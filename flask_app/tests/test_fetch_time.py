import re

from flask_app import fetch_time


def test_time_as_formatted_string():
    pattern = r'([1|2]\d{3})-((0[1-9])|(1[0-2]))-([0-2][0-9]|(3[0-1])) (([0-1]\d)|(2[0-3])):([0-5][0-9]):([0-5][0-9])'
    assert re.match(pattern, fetch_time.time_as_formatted_str())
