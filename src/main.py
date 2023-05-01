import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from log import clear_file, write_to_json
from parser import parse_course

def parse(department, course_number=None, shortened_reqs=False):
    # UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department}/courses.php"

    # Returns beautiful soup instance with children that are <div class="course">
    doc = BeautifulSoup(requests.get(url).content, "lxml", parse_only=SoupStrainer(class_="course"))

    # if no course nodes found, then throw error
    assert doc.find(id=course_number), f"Not a valid department: {department}"

    # clears log files
    clear_file("unmatched.txt")
    clear_file("unknown-reqs.txt")

    # if specific course number is specified ...
    if course_number:
        write_to_json("data.json", parse_course(doc.find(id=course_number), shortened_reqs))

    # otherwise parse the whole doc
    else:
        department_data = {}

        for node in doc:
            if isinstance(node, Tag):
                course_data = parse_course(node, shortened_reqs)
                department_data[course_data["number"]] = course_data

        write_to_json(f"{department}-data{'-short' if shortened_reqs else ''}.json", department_data)


parse("CSE", course_number=None, shortened_reqs=True)

