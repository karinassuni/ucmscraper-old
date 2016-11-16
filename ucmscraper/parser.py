import re
from datetime import datetime
from lxml import etree


RAW_FIELDS = ("crn", "cnum", "name", "stipulations", "units", "type", "days",
    "time", "location", "date_range", "seats_max", "seats_taken", "seats_left")


def parse(html, on_course_parsed=None):
    body = etree.HTML(html).xpath('//div[@class="pagebodydiv"]')[0]

    year = re.search('2[0-9]{3}$', body.findtext('h2')).group(0)
    department_tables = body.xpath('child::table[@class="datadisplaytable"]')
    department_names = body.xpath('child::h3/text()')

    # Cache XPaths
    # Exclude table headers
    tr_xpath = etree.XPath('descendant::tr[not(th)]')
    row_text_xpath = etree.XPath('descendant::node()/text()')
    href_xpath = etree.XPath('descendant::a/@href')

    courses = []

    for department, table in zip(department_names, department_tables):
        for i, row in enumerate(tr_xpath(table)):
            cell_texts = row_text_xpath(row)

            if "EXAM" in cell_texts:
                continue

            try:
                previous_course = courses[-1]
            except IndexError:
                pass
            else:
                has_no_crn = not str(cell_texts[RAW_FIELDS.index("crn")]).isdigit()
                if has_no_crn:
                    # This one course has multiple meeting times
                    # TODO: handle courses with multiple meeting times
                    continue

            try:
                course = parse_row(cell_texts, year)
            except:
                # TODO: logging
                continue

            course["department"] = department
            course["hyperlink"] = href_xpath(row)[0]

            if on_course_parsed:
                on_course_parsed(course)

            courses.append(course)

    return courses


def parse_row(row, year):
    course = dict()

    offset = 0

    for i, raw_field in enumerate(RAW_FIELDS):
        if raw_field == "stipulations":
            # Handle stipulations which increase the size of the array by 1 each
            possible_stipulation = row[i]
            if possible_stipulation.isdigit():
                # There's no stipulation, but we expect there to be one, so we must correct our indicies
                course["units"] = possible_stipulation
                offset = -1
            else:
                course["stipulations"] = possible_stipulation
                while not row[i + offset + 1].isdigit():
                    offset += 1
                    course["stipulations"] += "\n" + row[i + offset]
        elif raw_field == "time":
            # Split into start and end objects as attributes
            course["start"], course["end"] = to_time_objects(row[i + offset])
        elif raw_field == "date_range":
            # Split into isoformat strings
            start_date, end_date = row[i + offset].split(' ')

            course["start_date"] = to_iso_date(start_date, year)
            course["end_date"] = to_iso_date(end_date, year)
        else:
            course[raw_field] = row[i + offset]

    return course


def to_time_objects(time_range):
    """
    Returns a tuple of time objects given a time range string
    >>> to_time_objects("12:00-1:15pm")
        ({"hour": 12, "minute": 0}, {"hour": 13, "minute": 15})
    """
    start_str, end_str = time_range.split('-')

    if start_str == "TBD":
        assert end_str == "TBD"
        return "TBD", "TBD"

    start = dict()
    end = dict()

    start["hour"], start["minute"] = start_str.split(':')
    start["hour"] = int(start["hour"])
    start["minute"] = int(start["minute"])

    end["hour"], end["minute"] = end_str.split(':')
    end["hour"] = int(end["hour"])
    # Cut the 'pm' from end["minute"]
    end_meridiem = end["minute"][-2]
    end["minute"] = int(end["minute"][:-2])

    ends_in_afternoon = end_meridiem.startswith('p')
    starts_in_afternoon = ends_in_afternoon and start["hour"] < end["hour"] % 12

    if ends_in_afternoon:
        end["hour"] += 12
    if starts_in_afternoon:
        start["hour"] += 12

    return start, end


def to_iso_date(date, year):
    date += '-' + year
    return datetime.strptime(date, '%d-%b-%Y').date().isoformat()

