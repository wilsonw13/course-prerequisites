import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from typing import List

from req_parser import parse_course, parse_to_prereq_graph
from file_utils import get_from_json_dir, write_to_json_dir, clear_log_dir
from exceptions import DepartmentDoesNotExist

all_departments = get_from_json_dir("all_departments.json")


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
    write_to_json_dir("full_graph.json", graph)

    print("Written to './json/full_graph.json'")


if __name__ == "__main__":
    generate_full_graph()
