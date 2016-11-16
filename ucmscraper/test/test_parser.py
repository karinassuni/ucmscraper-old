import json
import os
import ucmscraper.parser as parser


def test_parse():
    this_module_dir = os.path.dirname(__file__)
    test_html_path = os.path.join(this_module_dir, 'spring17.html')
    html = open(test_html_path, "r").read()
    courses = parser.parse(html)
    with open(os.path.join(this_module_dir, 'spring17.json'), "r") as i:
        correct_courses = json.load(i)
    assert courses == correct_courses


def test_parse_row():
    pass


def test_to_time_objects():
    pass


def test_to_iso_date():
    pass
