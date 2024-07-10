import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from typing import List

from req_parser import parse_course
from file_utils import get_from_json_dir, write_to_json_dir, clear_log_dir
from exceptions import DepartmentDoesNotExist

# temp imports
from req_parser import Node

all_departments = get_from_json_dir("config/all_departments.json")


def get_course_bulletin(department: str):
    # SBU UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department.lower()}/courses.php"

    # Returns beautiful soup instance with children that are div tags with the course class
    doc = BeautifulSoup(requests.get(url).content, "lxml",
                        parse_only=SoupStrainer(class_="course"))

    # If a course tag can't be found, raise exception
    if not doc.find():
        raise DepartmentDoesNotExist(department)

    return doc


def department_parse(departments: List[str] = all_departments, reqs_ignore_non_courses: bool = False):
    data = {}

    clear_log_dir()

    for department in departments:
        try:
            doc = get_course_bulletin(department)

            for node in doc:
                if isinstance(node, Tag):
                    try:
                        course_data = parse_course(node, reqs_ignore_non_courses)
                        if course_data:
                            data[course_data["full_course_number"]] = course_data
                    except Exception as e:
                        print(f"Error parsing course: {e}")
        except DepartmentDoesNotExist as e:
            # Log any departments that don't exist
            e.log()

    return data


if __name__ == "__main__":
    data = department_parse(departments=["AMS", "CSE"], reqs_ignore_non_courses=True)
    write_to_json_dir("data/AMS_CSE_courses.json", data)
    write_to_json_dir("data/rules.txt", Node.gen_rules(), "txt")

    # data = department_parse(shortened_reqs=False)
    # write_to_json_dir("data/all_courses_full.json", data)

### queries
# given this course, what are all the prereqs?
# what courses have this course AND this course as a prereq?
# also check latex