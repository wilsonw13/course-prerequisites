import re
import unicodedata
from bs4 import Tag

from exceptions import UnknownRequisite, UnmatchedCourseLine

def match(regex: str, match_text: str, flags: re.RegexFlag = None):
    """Takes a regular expression, a text to match, and optional flags as input and returns a list of all non-overlapping matches in the text.

    Parameters
    ----------
    regex : str
        A string representing a regular expression pattern that you want to match against the match_text.
    match_text : str
        The text that we want to search for matches using the regular expression pattern specified in the regex parameter.
    flags : re.RegexFlag, optional
        The `flags` parameter is an optional argument that can be passed to the `re.findall()` method. It is used to modify the behavior of the regular expression pattern matching. The `flags` parameter is of type `re.RegexFlag`, which is an enumeration of various flag values that can be

    Returns
    -------
    list
        A list of all non-overlapping matches in the text. If no matches are found, the function returns an empty list.
    """

    if flags: text_match = re.findall(regex, match_text, flags)
    else: text_match = re.findall(regex, match_text)

    # if match is not found, return None
    if not text_match:
        return None

    # if regex is using capturing groups, return first match
    if isinstance(text_match[0], tuple):
        return text_match[0]

    # otherwise (if regex is not using capturing groups), return all matches
    else:
        return text_match

def req_match(txt: str, course_number: str):
    """Takes in a string and a dictionary, and returns a dictionary with information about the requisites specified in the string.

    Parameters
    ----------
    txt : str
        a string representing a requirement or prerequisite for a course
    course_number : str
        The `data` parameter is a dictionary containing information about a course, including its department code (`department`) and course number (`number`). This information is used in the function to provide context for parsing the course requisites.

    Returns
    -------
    dict
        a dictionary containing information about the requisites specified in the string
    """

    # cleans txt
    txt = txt.strip()
    # if txt is an empty string, return
    if not txt: return

    # removes the "C or higher/better" from txt
    if match(r"[ABCD][+-]? or (?:higher|better)(?:\s?in|:)\s*", txt):
        txt = match(r"[ABCD][+-]? or (?:higher|better)(?:\s?in|:)\s*(.*)", txt)[0]

    # if there is an "and" or ";"
    if match(r"(?:\sand\s|;)", txt, re.IGNORECASE):
        or_split_txt = re.split(r"(?:\sand\s|;)", txt)

        # if first txt in split_txt is a course
        if match(r"[a-zA-Z]{3}\s?\d{3}", or_split_txt[0]):

            for i, t in enumerate(or_split_txt):
                # if t does not have department code, then add it from the previous element
                if match(r"^(?:(?![a-zA-Z]{3}).)*$", t):
                    or_split_txt[i] = f"{match(r'[a-zA-Z]{3}', or_split_txt[i - 1])[0]} {t}"

        return {
            "type": "and",
            "value": [req_match(t, course_number) for t in or_split_txt]
        }

    # if txt is majors and contains major codes such as CSE, AMS, etc.
    if match(r"major", txt, re.IGNORECASE) and match(r"([A-Z]{3})", txt):
        return {"type": "major", "value": [x for x in match(r"([A-Z]{3})", txt)]}


    # if txt is standing
    if match(r"standing", txt, re.IGNORECASE):
        return {"type": "standing", "value": min([int(x) for x in match(r"U(\d+)", txt)])}

    # if txt is math placement exam
    if match(r"math.*placement\sexam", txt, re.IGNORECASE):
        return {"type": "math placement", "value": min([int(x) for x in match(r"level\s(\d+)", txt, re.IGNORECASE)])}

    # if txt is any of the (CEAS) honors programs
    if match(r"(?:honors|university\sscholars)", txt, re.IGNORECASE):
        honors_programs = []

        if match(r"computer\sscience\shonors", txt, re.IGNORECASE): honors_programs.append("CS Honors")
        if match(r"honors\scollege", txt, re.IGNORECASE): honors_programs.append("Honors College")
        if match(r"wise\shonors", txt, re.IGNORECASE): honors_programs.append("WISE")
        if match(r"university\sscholars", txt, re.IGNORECASE): honors_programs.append("University Scholars")

        if not honors_programs: print(f"{course_number}: Unknown Honors Program: {txt}")

        return {"type": "honors", "value": honors_programs}

    # if there is an "or" | SAME CODE AS "AND"
    if match(r"\sor\s", txt, re.IGNORECASE):
        or_split_txt = re.split(r"\sor\s", txt)

        # if first txt in split_txt is a course
        if match(r"[a-zA-Z]{3}\s?\d{3}", or_split_txt[0]):

            for i, t in enumerate(or_split_txt):
                # if t does not have department code, then add it from the previous element
                if match(r"^(?:(?![a-zA-Z]{3}).)*$", t):
                    or_split_txt[i] = f"{match(r'[a-zA-Z]{3}', or_split_txt[i - 1])[0]} {t}"

        return {
            "type": "or",
            "value": [req_match(t, course_number) for t in or_split_txt]
        }

    # if txt is a course
    if match(r"^[a-zA-Z]{3}\s\d{3}$", txt):
        return {"type": "course", "value": txt}

    try:
        raise UnknownRequisite(txt, course_number)
    except UnknownRequisite as e:
        e.log()
        return {"type": "custom", "value": txt}

def simple_req_match(txt: str, course_number: str):
    """Extracts course codes from a given string and adds missing department codes if necessary.

    Parameters
    ----------
    txt : str
        a string containing course codes
    course_number : str
        The "data" parameter is a dictionary that is not used in the given function. It is likely meant to contain some information related to courses or requirements, but without more context it is impossible to say for sure.

    Returns
    -------
    list
        a list of course codes
    """

    req_courses = match(r"([A-Z]{3}\s\d{3}|\d{3})", txt)

    try:
        if req_courses:
            for i, c in enumerate(req_courses):
                # if t does not have department code, then add it from the previous element
                if not match(r"[A-Z]{3}", c):
                    if i == 0:
                        raise UnknownRequisite(txt, course_number)
                    else:
                        req_courses[i] = f"{match(r'[a-zA-Z]{3}', req_courses[i - 1])[0]} {c}"
        else: raise UnknownRequisite(txt, course_number)
    except UnknownRequisite as e:
        e.log()

    return req_courses

def parse_course(course_node, parse_simple_reqs: bool = False):
    """Parses course information from a webpage and returns a dictionary containing various details about the course.

    Parameters
    ----------
    course_node
        It is a BeautifulSoup object representing a single course
    parse_simple_reqs : bool, optional
        A boolean value that indicates whether the function should simply parse reqs. The default value is False.

    Returns
    -------
    dict
        A dictionary containing various details about the course. The dictionary contains the following keys:
        - "department": the three-letter department code of the course (e.g. "CSE")
        - "number": the three-digit course number (e.g. "101")
        - "full_course_number": the three-letter department code followed by the three-digit course number (e.g. "CSE 101")
        - "name": the name of the course (e.g. "Introduction to Computer Science")
        - "description": a description of the course
        - "prerequisites": a list of prerequisites for the course
        - "corequisites": a list of corequisites for the course
        - "antirequisites": a list of antirequisites for the course
        - "advisoryPrerequisites": a list of advisory prerequisites for the course
        - "advisoryCorequisites": a list of advisory corequisites for the course
        - "sbcs": a list of SBCs that the course satisfies
        - "credits": the number of credits that the course is worth
    """

    # default data object
    course_data = {
        "department": None,
        "number": None,
        "full_course_number": None,
        "name": None,
        "description": None,
        "prerequisites": None,
        "corequisites": None,
        "antirequisites": None,
        "advisoryPrerequisites": None,
        "advisoryCorequisites": None,
        "sbcs": None,
        "credits": None,
    }

    for lineI, line in enumerate(course_node.children):
        # cleans up text by replacing all /n and multiple consecutive spaces with a single space and normalizes unicode
        text = unicodedata.normalize("NFKD", re.sub(r"\s{2,}", " ", line.text.replace("\n", " ")).strip())

        # if line is an empty line or is an empty element (of class "clear"), continue to next line
        if not text or (isinstance(line, Tag) and line.attrs.get("class") == ["clear"]): continue

        # if line is first (then it specifies the headers)
        if lineI == 1:
            (course_data["department"], course_data["number"], course_data["name"]) = match(r"^([a-zA-Z]{3})\s(\d{3}):\s*(.*)$", text)
            course_data["full_course_number"] = course_data["department"] + " " + course_data["number"]

        # if line is second (then it specifies the description)
        elif lineI == 3:
            course_data["description"] = text

        # if line matches SBC
        elif match(r"SBC:", text):
            # matches all SBCs if any
            sbcs = re.findall(r"SBC:\s*([A-Z]+(?:,\s*[A-Z]+)*)", text)
            course_data["sbcs"] = sbcs if sbcs else []

        # if line matches partial fulfillment of SBCs
        elif match(r"Partially fulfills", text): continue

        # if line is an SBC
        elif isinstance(line, Tag) and line.name == "a" and line.has_attr("title"):
            course_data["sbcs"].append(text)

        # if line matches credits
        elif match(r"(\d+(?:-\d+)?)\scredits?", text):
            course_data["credits"] = match(r"(\d+(?:-\d+)?)\scredits?", text)[0]

        # if line matches requisite
        elif match(r"requisite", text):
            (req_type, req_text) = match(r"(.*)requisites?:\s*(.*)$", text)

            # clean up requisite_type
            req_type = re.sub(r"\s+", " ", req_type.replace("-", " ").lower().strip())

            requisite_obj = simple_req_match(req_text, course_data['full_course_number']) if parse_simple_reqs else req_match(req_text, course_data['full_course_number'])

            if req_type == "pre":
                course_data["prerequisites"] = requisite_obj
            elif req_type == "co":
                course_data["corequisites"] = requisite_obj
            elif req_type == "pre or co":
                course_data["prerequisites"] = course_data["corequisites"] = requisite_obj
            elif req_type == "anti":
                course_data["antirequisites"] = requisite_obj
            elif req_type == "advisory pre":
                course_data["advisoryPrerequisites"] = requisite_obj
            elif req_type == "advisory co":
                course_data["advisoryCorequisites"] = requisite_obj
            elif req_type == "advisory pre or co":
                course_data["advisoryPrerequisites"] = course_data["advisoryCorequisites"] = requisite_obj
            else:
                print(f"\"{req_type}\" is not a valid requisite type")

        # otherwise (if line doesn't match) ...
        else:
            try: raise UnmatchedCourseLine(text, course_data['full_course_number'])
            except UnmatchedCourseLine as e: e.log()

    return course_data

def parse_to_prereq_graph(course_node, data: dict, department_exceptions: list, group_num: int):
    course_number = None

    for lineI, line in enumerate(course_node.children):
        try:
            # cleans up text by replacing all /n and multiple consecutive spaces with a single space and normalizes unicode
            text = unicodedata.normalize("NFKD", re.sub(r"\s{2,}", " ", line.text.replace("\n", " ")).strip())

            # if line is an empty line or is an empty element (of class "clear"), continue to next line
            if not text or (isinstance(line, Tag) and line.attrs.get("class") == ["clear"]): continue

            # if line is first (then it specifies the headers)
            if lineI == 1:
                course_number, name = match(r"^([A-Z]{3}\s\d{3}):\s*(.*)", text)

                # append the course as a node (to future graph)
                data["nodes"].append({
                    "id": course_number,
                    "name": name,
                    "group": group_num
                })

            # if line matches requisite
            elif match(r"requisite", text):
                assert course_number, "course has not been found!"

                try:
                    (req_type, req_text) = match(r"(.*)requisite\(?s?\)?:\s*(.*)$", text)
                except TypeError:
                    raise UnknownRequisite(text, course_number)

                # clean up requisite_type
                req_type = re.sub(r"\s+", " ", req_type.replace("-", " ").lower().strip())

                reqs = simple_req_match(req_text, course_number)

                if reqs and not match("advisory", req_type) and match("pre", req_type):
                    for req in reqs:
                        if req[0:3] not in department_exceptions:
                            data["links"].append({
                                "source": req,
                                "target": course_number
                            })

        except UnknownRequisite as e:
            e.log()

