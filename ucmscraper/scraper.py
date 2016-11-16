import requests
from lxml import etree
from ucmscraper.parser import parse


URL = 'https://pbanssb.ucmerced.edu/pls/PROD/xhwschedule.p_selectsubject'


def get_term_courses(term_code, on_course_parsed=None):
    payload = {
        "validterm": term_code,
        # All classes, not just open classes
        "openclasses": "N",
        # All subjects/departments
        "subjcode": "ALL"
    }

    return parse(requests.post(URL, data=payload).content, on_course_parsed)


def scrape_all_terms(on_term_parsed=None, on_course_parsed=None):
    term_select_page = requests.get(URL).content
    term_radio_buttons = etree.HTML(term_select_page).xpath('//form/descendant::input[@name="validterm"]')
    for t in term_radio_buttons:
        term = t.get("value")
        courses = get_term_courses(term, on_course_parsed)
        on_term_parsed(term, courses)


def scrape_latest_term(on_course_parsed=None):
    term_select_page = requests.get(URL).content
    term_radio_buttons = etree.HTML(term_select_page).xpath('//form/descendant::input[@name="validterm"]')
    latest_term = term_radio_buttons[-1].get("value")
    return get_term_courses(latest_term, on_course_parsed)
