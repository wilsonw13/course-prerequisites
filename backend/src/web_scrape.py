import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from typing import List

from req_parser import parse_course, parse_to_prereq_graph
from file_utils import get_from_json_dir, write_to_json_dir, clear_log_dir
from exceptions import DepartmentDoesNotExist

all_departments = get_from_json_dir("config/all_departments.json")


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


def department_parse(departments: List[str] = all_departments, shortened_reqs: bool = False, reqs_ignore_non_courses: bool = False):
    data = {}

    clear_log_dir()

    for department in departments:
        try:
            doc = get_course_bulletin(department)

            for node in doc:
                if isinstance(node, Tag):
                    # try:
                        course_data = parse_course(node, shortened_reqs, reqs_ignore_non_courses)
                        data[course_data["full_course_number"]] = course_data
                    # except Exception as e:
                    #     print(f"Error parsing course: {e}")
        except DepartmentDoesNotExist as e:
            # Log any departments that don't exist
            e.log()

    return data


def generate_full_graph(departments: List[str] = all_departments):
    """Generates a graph representation of all courses and their prerequisites by calling get_course_bulletin() to web scrape. Writes the resulting graph to a JSON file.

    Parameters
    ----------
    departments : List[str], optional
        The list of departments to generate the graph for. The default value is all departments.
    """

    # remove_links: bool = True

    departments_docs = []
    department_exceptions = []

    clear_log_dir()  # Clear the log directory before starting

    for department in departments:
        try:
            # Get the course bulletin for each department
            departments_docs.append(get_course_bulletin(department))
        except DepartmentDoesNotExist as e:
            # Log any departments that don't exist
            department_exceptions.append(e.department)
            e.log()

    # Make sure there are courses to visualize
    assert departments_docs, "No department courses found!"

    graph = {
        "courses_name_pair": [],
        "prereqs": []
    }

    for doc in departments_docs:
        # TODO: why is there a index 1 here?
        for node in doc:
            if isinstance(node, Tag):
                # Parse the course data into a graph
                parse_to_prereq_graph(node, graph, department_exceptions)

    # if remove_links:  # Remove links that don't have a corresponding course node
    course_graph_nodes = [node[0] for node in graph["courses_name_pair"]]
    graph["prereqs"] = [link for link in graph["prereqs"]
                        if link[0] in course_graph_nodes]
    # else:  # Add courses as nodes even if they don't have any prerequisites
    # pass

    # Write the graph data to a JSON file
    write_to_json_dir("data/full_graph.json", graph)

    print("Written to './json/data/full_graph.json'")


if __name__ == "__main__":
    data = department_parse(departments=["AMS", "CSE"], reqs_ignore_non_courses=True)
    write_to_json_dir("data/AMS_CSE_courses.json", data)

    # data = department_parse(shortened_reqs=False)
    # write_to_json_dir("data/all_courses_full.json", data)

#     prereqs = {course_id: course["prerequisites"]
#                for course_id, course
#                in get_from_json_dir("data/all_courses.json").items()
#                if course["prerequisites"]}
#
#     write_to_json_dir("data/all_prereqs.json", prereqs)
