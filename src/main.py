from bs4 import BeautifulSoup, SoupStrainer, Tag
from log import clear_file, write_to_json
from parser import parse_course

with open("../cse.html") as file:
    doc = BeautifulSoup(file, "lxml", parse_only=SoupStrainer(class_="course"))

clear_file("unmatched.txt")
clear_file("unknown-reqs.txt")

def parse_document():
    department_data = {}

    for node in doc:
        if isinstance(node, Tag):
            course_data = parse_course(node)
            department_data[course_data["number"]] = course_data

    write_to_json("data.json", department_data)

def parse_single_course(course_id):
    write_to_json("data.json", parse_course(doc.find(id=course_id)))


parse_document()
# parse_single_course("495")


