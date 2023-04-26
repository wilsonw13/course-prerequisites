import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from log import clear_file, write_to_json
from parser import parse_course

def parse(department, course_number=None):
    # UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department}/courses.php"

    # Returns beautiful soup
    doc = BeautifulSoup(requests.get(url).content, "lxml", parse_only=SoupStrainer(class_="course"))

    clear_file("unmatched.txt")
    clear_file("unknown-reqs.txt")

    # if specific course number is specified ...
    if course_number:
        write_to_json("data.json", parse_course(doc.find(id=course_number)))

    else:
        department_data = {}

        for node in doc:
            if isinstance(node, Tag):
                course_data = parse_course(node)
                department_data[course_data["number"]] = course_data

        write_to_json("data.json", department_data)


parse("a", course_number="131")

# with open("../lin.html") as file:
#     doc = BeautifulSoup(file, "lxml", parse_only=SoupStrainer(class_="course"))

# def parse_document():
#     department_data = {}
#
#     for node in doc:
#         if isinstance(node, Tag):
#             course_data = parse_course(node)
#             department_data[course_data["number"]] = course_data
#
#     write_to_json("data.json", department_data)
#
# def parse_single_course(course_id):
#     write_to_json("data.json", parse_course(doc.find(id=course_id)))


# parse_document()
# parse_single_course("")

