import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag

from req_parser import parse_course
from file_utils import write_to_json_dir, clear_log_dir
from exceptions import DepartmentDoesNotExist


def get_course_bulletin(department: str):
    # SBU UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department}/courses.php"

    # Returns beautiful soup instance with children that are div tags with the course class
    doc = BeautifulSoup(requests.get(url).content, "lxml",
                        parse_only=SoupStrainer(class_="course"))

    # If a course tag can't be found, raise exception
    if not doc.find():
        raise DepartmentDoesNotExist(department)

    return doc


def full_parse(department: str, course_number: str = "", shortened_reqs: bool = False):
    doc = get_course_bulletin(department)

    clear_log_dir()

    # if specific course number is specified ...
    if course_number:
        write_to_json_dir("data.json", parse_course(
            doc.find(id=course_number), shortened_reqs))

    # otherwise parse the whole doc
    else:
        department_data = {}

        for node in doc:
            if isinstance(node, Tag):
                course_data = parse_course(node, shortened_reqs)
                department_data[course_data["number"]] = course_data

        write_to_json_dir(
            f"{department}-data{'-short' if shortened_reqs else ''}.json", department_data)
