import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from req_parser import match, parse_course, parse_to_prereq_graph
from file_utils import write_to_datasets_json, get_datasets_json, clear_log_dir
from exceptions import DepartmentDoesNotExist

all_departments = [
    "AAS",
    "ACC",
    "AFH",
    "AFS",
    "AIM",
    "AMR",
    "AMS",
    "ANP",
    "ANT",
    "ARB",
    "ARH",
    "ARS",
    "ASC",
    "AST",
    "ATM",
    "BCP",
    "BIO",
    "BME",
    "BUS",
    "CAR",
    "CCS",
    "CDS",
    "CDT",
    "CEF",
    "CHE",
    "CHI",
    "CIV",
    "CLL",
    "CLS",
    "CLT",
    "CME",
    "COM",
    "CSE",
    "CWL",
    "DAN",
    "DIA",
    "EAS",
    "EBH",
    "ECO",
    "EDP",
    "EEL",
    "EEO",
    "EGL",
    "ENS",
    "ENV",
    "ESE",
    "ESG",
    "ESM",
    "EST",
    "EUR",
    "EXT",
    "FLA",
    "FLM",
    "FRN",
    "GEO",
    "GER",
    "GLI",
    "GRK",
    "GSS",
    "HAD",
    "HAL",
    "HAN",
    "HAT",
    "HBA",
    "HBH",
    "HBM",
    "HBP",
    "HBW",
    "HBY",
    "HDG",
    "HDO",
    "HDP",
    "HIN",
    "HIS",
    "HNC",
    "HND",
    "HNG",
    "HNH",
    "HNI",
    "HON",
    "HUE",
    "HUF",
    "HUG",
    "HUI",
    "HUL",
    "HUR",
    "HUS",
    "HWC",
    "IAE",
    "IAP",
    "INT",
    "ISE",
    "ITL",
    "JDH",
    "JDS",
    "JPN",
    "JRN",
    "KOR",
    "LAC",
    "LAN",
    "LAT",
    "LCR",
    "LDR",
    "LHD",
    "LHW",
    "LIA",
    "LIN",
    "MAE",
    "MAP",
    "MAR",
    "MAT",
    "MDA",
    "MEC",
    "MSL",
    "MUS",
    "MVL",
    "NUR",
    "OAE",
    "PER",
    "PHI",
    "PHY",
    "POL",
    "POR",
    "PSY",
    "RLS",
    "RUS",
    "SBU",
    "SCH",
    "SCI",
    "SKT",
    "SLN",
    "SOC",
    "SPN",
    "SSE",
    "SUS",
    "SWA",
    "THR",
    "TRK",
    "TVW",
    "UKR",
    "VIP",
    "WAE",
    "WRT",
    "WSE",
    "WST"
]

def get_course_bulletin(department: str):
    # SBU UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department}/courses.php"

    # Returns beautiful soup instance with children that are div tags with the course class
    doc = BeautifulSoup(requests.get(url).content, "lxml", parse_only=SoupStrainer(class_="course"))

    # If a course tag can't be found, raise exception
    if not doc.find(): raise DepartmentDoesNotExist(department)

    return doc

def full_parse(department: str, course_number: str = None, shortened_reqs: bool = False):
    doc = get_course_bulletin(department)

    clear_log_dir()

    # if specific course number is specified ...
    if course_number:
        write_to_datasets_json("data.json", parse_course(doc.find(id=course_number), shortened_reqs))

    # otherwise parse the whole doc
    else:
        department_data = {}

        for node in doc:
            if isinstance(node, Tag):
                course_data = parse_course(node, shortened_reqs)
                department_data[course_data["number"]] = course_data

        write_to_datasets_json(f"{department}-data{'-short' if shortened_reqs else ''}.json", department_data)


def generate_3d_visualization_json(departments: list[str], remove_links: bool = True):
    departments_docs = []
    department_exceptions = []

    clear_log_dir()

    for department in departments:
        try:
            departments_docs.append(get_course_bulletin(department))
        except DepartmentDoesNotExist as e:
            department_exceptions.append(e.department)
            e.log()

    assert departments_docs, "No department courses found!"

    graph_data = {
        "nodes": [],
        "links": []
    }

    for i, doc in enumerate(departments_docs):
        for node in doc:
            if isinstance(node, Tag): parse_to_prereq_graph(node, graph_data, department_exceptions, i + 1)

    # whenever a course in a link's source is not found in node...
    if remove_links:  # remove the link
        course_graph_nodes = [node["id"] for node in graph_data["nodes"]]
        graph_data["links"] = [link for link in graph_data["links"] if link["source"] in course_graph_nodes]
    else:  # add the course as another node
        pass

    write_to_datasets_json("graph-data.json", graph_data)

def query_prerequisite_graph(
        courses: list[str] = None,
        departments: list[str] = None,
        show_direct_prerequisites: bool = False,
        show_transitive_prerequisites: bool = False,
        show_disconnected_courses: bool = True
):
    graph_data = get_datasets_json("full-graph-data.json")
    assert graph_data, "No graph data found!"

    print (courses, departments, show_disconnected_courses)

    # gets a set of all course names in nodes (will be used later as the set of queried nodes)
    node_ids = {node["id"] for node in graph_data["nodes"]}

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
        if not node_ids: raise Exception("No matching courses found from course/department!")

        # if show_transitive_prerequisites:  should be if/elif/else --- USE LOGIC RULES HERE
        if show_direct_prerequisites:
            # making set of all courses that appear in links that direct to a queried course
            link_source_ids = {link["source"] for link in graph_data["links"] if link["target"] in node_ids}
            graph_data["nodes"] = [node for node in graph_data["nodes"]
                                   if node["id"] in node_ids or node["id"] in link_source_ids]
            graph_data["links"] = [link for link in graph_data["links"]
                                   if link["target"] in node_ids]
        else:
            graph_data["nodes"] = [node for node in graph_data["nodes"] if node["id"] in node_ids]
            graph_data["links"] = [link for link in graph_data["links"]
                                   if link["source"] in node_ids and link["target"] in node_ids]

    # will not remove disconnected courses if there are no links (i.e. all queried courses are disconnected)
    if not show_disconnected_courses and graph_data["links"]:
        # gets a list of all courses found in links
        courses_in_links = {link["source"] for link in graph_data["links"]} | {link["target"] for link in graph_data["links"]}

        graph_data["nodes"] = [node for node in graph_data["nodes"] if node["id"] in courses_in_links]

    write_to_datasets_json("queried-graph-data.json", graph_data)

    return graph_data


# full_parse("CSE", course_number=None, shortened_reqs=False)
# generate_3d_visualization_json(all_departments)
# generate_3d_visualization_json(["CSE", "AMS"])
# query_prerequisite_graph(courses=[],
#                          departments=["CSE", "AMS"],
#                          show_direct_prerequisites=True,
#                          show_disconnected_courses=True)
