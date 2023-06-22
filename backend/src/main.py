from bs4 import Tag
from inspect import signature
from typing import List
import re

from web_scrape import get_course_bulletin
from req_parser import parse_to_prereq_graph
from file_utils import write_to_datasets_json, get_datasets_json, clear_log_dir
from exceptions import DepartmentDoesNotExist

all_departments = get_datasets_json("all_departments.json")


def generate_3d_visualization(departments: List[str] = all_departments, remove_links: bool = True):
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

    graph_data = {
        "nodes": [],
        "links": []
    }

    for i, doc in enumerate(departments_docs):
        for node in doc:
            if isinstance(node, Tag):
                # Parse the course data into a graph
                parse_to_prereq_graph(
                    node, graph_data, department_exceptions, i + 1)

    if remove_links:  # Remove links that don't have a corresponding course node
        course_graph_nodes = [node["course_number"]
                              for node in graph_data["nodes"]]
        graph_data["links"] = [link for link in graph_data["links"]
                               if link["source"] in course_graph_nodes]
    else:  # Add courses as nodes even if they don't have any prerequisites
        pass

    # Write the graph data to a JSON file
    write_to_datasets_json("full_graph_data.json", graph_data)


def query_prerequisite_graph(
        courses: List[str] = [],
        departments: List[str] = [],
        show_direct_prerequisites: bool = False,
        show_transitive_prerequisites: bool = False,
        show_disconnected_courses: bool = True
):
    graph_data = get_datasets_json("full_graph_data.json")
    assert graph_data, "No graph data found!"

    print(courses, departments, show_disconnected_courses)

    # gets a set of all course names in nodes (will be used later as the set of queried nodes)
    node_ids = {node["course_number"] for node in graph_data["nodes"]}

    if courses or departments:
        # filters courses to only include those of the specified course/department (found in either)
        if courses and departments:
            node_ids = {course for course in node_ids if
                        course[:3] in departments or
                        course in courses}
        else:
            node_ids = {course for course in node_ids if
                        (not departments or course[:3] in departments) and
                        (not courses or course in courses)}
        if not node_ids:
            raise Exception(
                "No matching courses found from course/department!")

        # if show_transitive_prerequisites:  should be if/elif/else --- USE LOGIC RULES HERE
        if show_direct_prerequisites:
            # making set of all courses that appear in links that direct to a queried course
            link_source_ids = {
                link["source"] for link in graph_data["links"] if link["target"] in node_ids}
            graph_data["nodes"] = [node for node in graph_data["nodes"]
                                   if node["course_number"] in node_ids or node["course_number"] in link_source_ids]
            graph_data["links"] = [link for link in graph_data["links"]
                                   if link["target"] in node_ids]
        else:
            graph_data["nodes"] = [
                node for node in graph_data["nodes"] if node["course_number"] in node_ids]
            graph_data["links"] = [link for link in graph_data["links"]
                                   if link["source"] in node_ids and link["target"] in node_ids]

    # will not remove disconnected courses if there are no links (i.e. all queried courses are disconnected)
    if not show_disconnected_courses and graph_data["links"]:
        # gets a list of all courses found in links
        courses_in_links = {link["source"] for link in graph_data["links"]} | {
            link["target"] for link in graph_data["links"]}

        graph_data["nodes"] = [node for node in graph_data["nodes"]
                               if node["course_number"] in courses_in_links]

    write_to_datasets_json("queried_graph_data.json", graph_data)

    return graph_data


def get_params(func):
    return [list(match) for match in re.findall(r'(\w+):\s*([\w\[\]]+)(?:\s*=\s*([\w\d\[\]\'\"]+))?', str(signature(func)))]

# generate_3d_visualization(all_departments)
# generate_3d_visualization(["CSE", "AMS"])
# query_prerequisite_graph(courses=[],
#                          departments=["CSE", "AMS"],
#                          show_direct_prerequisites=True,
#                          show_disconnected_courses=True)
