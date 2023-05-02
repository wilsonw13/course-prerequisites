import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from log import clear_file, write_to_json
from parser import parse_course, parse_for_3d_visualization

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

department_exceptions = [
    "AFH",
    "AIM",
    "AMR",
    "ANP",
    "ARB",
    "ARS",
    "ASC",
    "BCP",
    "CAR",
    "CCS",
    "CDS",
    "CDT",
    "CEF",
    "CHI",
    "CLL",
    "CLT",
    "DAN",
    "EAS",
    "EEL",
    "ENV",
    "EST",
    "EUR",
    "EXT",
    "FLA",
    "GER",
    "GRK",
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
    "JDH",
    "JPN",
    "LAN",
    "LAT",
    "LCR",
    "LDR",
    "LHD",
    "LHW",
    "LIA",
    "MAE",
    "MAP",
    "MDA",
    "MSL",
    "MVL",
    "NUR",
    "OAE",
    "PER",
    "POR",
    "SBU",
    "SCH",
    "SCI",
    "SKT",
    "SLN",
    "SSE",
    "SWA",
    "TRK",
    "UKR",
    "VIP",
    "WAE",
    "WSE"
]

def get_course_bulletin(department: str, course_number: str = None):
    # UG Bulletin Link
    url = f"https://www.stonybrook.edu/sb/bulletin/current/academicprograms/{department}/courses.php"

    # Returns beautiful soup instance with children that are <div class="course">
    doc = BeautifulSoup(requests.get(url).content, "lxml", parse_only=SoupStrainer(class_="course"))

    try:
        # if no course nodes found, then throw error
        assert doc.find(id=course_number), f"Not a valid department: {department}"
    except AssertionError:
        print(f"{department} not found")

    # clears log files
    clear_file("unmatched.txt")
    clear_file("unknown-reqs.txt")

    return doc


def full_parse(department: str, course_number: str = None, shortened_reqs: bool = False):
    doc = get_course_bulletin(department, course_number)

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


def generate_3d_visualization_json(departments: list[str], department_exceptions: list[str]):
    data = {
        "nodes": [],
        "links": []
    }

    for i, department in enumerate(departments):
        doc = get_course_bulletin(department)

        for node in doc:
            if isinstance(node, Tag): parse_for_3d_visualization(node, data, department_exceptions, i + 1)

    write_to_json(f"all-3d-visual.json", data)


# full_parse("CSE", course_number=None, shortened_reqs=True)
generate_3d_visualization_json(all_departments, department_exceptions)

# nodes that i had to add:
# MAT 141, 142, 171, 205, 305
# ANT 304
# CHE 141, 326, 341
# 
# gave up manually adding nodes, so wrote some quick js to do it for me

