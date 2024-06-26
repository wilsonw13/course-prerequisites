import re
import unicodedata
import secrets
import string
from bs4 import Tag
from typing import List

from exceptions import UnknownRequisite, UnmatchedCourseLine

FULL_COURSE_NUMBER_REGEX = r"[a-zA-Z]{3}\s?\d{3}"
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

    if flags:
        text_match = re.findall(regex, match_text, flags)
    else:
        text_match = re.findall(regex, match_text)

    # if match is not found, return None
    if not text_match:
        return None

    # if regex is using capturing groups, return first match
    if isinstance(text_match[0], tuple):
        return text_match[0]

    # otherwise (if regex is not using capturing groups), return all matches
    else:
        return text_match

class Temp_Parent:
    ids = set() # not inherited
    set_ = set()

    def __init__(self) -> None:
        """
        base_id: the generated id that uniquely identifies that tuple
        child_id: the child id of the tuple
        """
        self.base_id = None
        self.child_base_id = None
        self.__class__.set_.add(self) # add to the unique tuple set

    def full_id(self, id_) -> str:
        prefix = None

        if isinstance(self, And_):
            prefix = "a"
        elif isinstance(self, Member):
            prefix = "m"
        else:
            print("Invalid class: {self}")
            return None

        return f"{prefix}_{id_}" if not match(FULL_COURSE_NUMBER_REGEX, id_) else id_

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.full_id(self.base_id)}, {self.full_id(self.child_base_id)})"

    ### Static Methods
    @staticmethod
    def generate_id() -> str:
        DEFAULT_ID_LENGTH = 6
        while True:
            id_ = ''.join(secrets.choice(string.ascii_letters + string.digits)
                          for _ in range(DEFAULT_ID_LENGTH))
            if id_ not in Temp_Parent.ids:
                Temp_Parent.ids.add(id_)
                return id_

    @staticmethod
    def readable_format() -> str:
        return "\n".join(map(str, And_.set_.union(Or_.set_).union(Member.set_)))


class And_(Temp_Parent):
    def __init__(self, children, parent_id=None) -> None:
        if not children:
            print("Invalid And_ created")
            return

        super().__init__()

        self.base_id = parent_id or Temp_Parent.generate_id()
        self.child_base_id = Member.create(children) if len(children) > 1 else children[0]


class Or_(Temp_Parent):
    def __init__(self, children, parent_id=None) -> None:
        if not children:
            print("Invalid Or_ created")
            return

        super().__init__()

        self.base_id = parent_id or Temp_Parent.generate_id()
        self.child_base_id = Member.create(children) if len(children) > 1 else children[0]


class Member(Temp_Parent):
    def __init__(self, base_id, member_id) -> None:
        if not (base_id and member_id):
            print("Invalid Member created")
            return

        super().__init__()

        self.base_id = base_id
        self.child_base_id = member_id

    # create member tuples from a list of values
    @staticmethod
    def create(values) -> str:
        member_id = Temp_Parent.generate_id()

        for val in values:
            Member(member_id, val)

        return member_id



def req_match(txt: str, course_number: str, parent_id: str, ignore_non_courses: bool = False):
    """Takes in a string and a dictionary, and returns a dictionary with information about the requisites specified in the string.

    Parameters
    ----------
    txt : str
        a string representing a requirement or prerequisite for a course
    course_number : str
        The `data` parameter is a dictionary containing information about a course, including its department code (`department`) and course number (`number`). This information is used in the function to provide context for parsing the course requisites.
    reqs_ignore_non_courses : bool, optional
        A boolean value that indicates whether or not to ignore prequisites that are not other courses

    Returns
    -------
    dict
        a dictionary containing information about the requisites specified in the string
    """

    # cleans txt
    txt = txt.strip()
    # if txt is an empty string, return
    if not txt:
        return

    # removes the "C or higher/better" from txt
    if match(r"[ABCD][+-]? or (?:higher|better)(?:\s?in|:)\s*", txt):
        txt = match(
            r"[ABCD][+-]? or (?:higher|better)(?:\s?in|:)\s*(.*)", txt)[0]

    # if there is an "and" or ";"
    if match(r"(?:\sand\s|;)", txt, re.IGNORECASE):
        split_txt = re.split(r"(?:\sand\s|;)", txt)

        # if first txt in split_txt is a course
        if match(FULL_COURSE_NUMBER_REGEX, split_txt[0]):
            for i, t in enumerate(split_txt):
                # if t does not have department code, then add it from the previous element
                if match(r"^(?:(?![a-zA-Z]{3}).)*$", t):
                    split_txt[i] = f"{match(r'[a-zA-Z]{3}', split_txt[i - 1])[0]} {t}"

        if not ignore_non_courses:
            # TODO fix later
            return {
                "type": "and",
                "value": [req_match(t, course_number, ignore_non_courses) for t in split_txt]
            }

        # if non-courses are ignored, then we must remove all the Nones present
        values = list(filter(lambda x: x is not None, [req_match(t, course_number, "whatisthis_and", ignore_non_courses) for t in split_txt]))

        instance = And_(values, parent_id)
        return instance.full_id(instance.base_id)

    # if txt is majors and contains major codes such as CSE, AMS, etc.
    if match(r"major", txt, re.IGNORECASE) and match(r"([A-Z]{3})", txt):
        if ignore_non_courses: return None
        return {"type": "major", "value": [x for x in match(r"([A-Z]{3})", txt)]}

    # if txt is standing
    if match(r"standing|status", txt, re.IGNORECASE):
        if ignore_non_courses: return None
        standings = {
            "freshmen": 1,
            "sophomore": 2,
            "junior": 3,
            "senior": 4
        }

        for standing, val in standings.items():
            if match(standing, txt, re.IGNORECASE):
                return {"type": "standing", "value": val}

        return {"type": "standing", "value": min([int(x) for x in match(r"U(\d+)", txt)])}

    # if txt is math placement exam
    if match(r"math.*placement\sexam", txt, re.IGNORECASE):
        if ignore_non_courses: return None
        return {"type": "math placement", "value": min([int(x) for x in match(r"level\s(\d+)", txt, re.IGNORECASE)])}

    # if txt is any of the (CEAS) honors programs
    if match(r"(?:honors|university\sscholars)", txt, re.IGNORECASE):
        if ignore_non_courses: return None

        honors_programs = []

        if match(r"computer\sscience\shonors", txt, re.IGNORECASE):
            honors_programs.append("CS Honors")
        if match(r"honors\scollege", txt, re.IGNORECASE):
            honors_programs.append("Honors College")
        if match(r"wise\shonors", txt, re.IGNORECASE):
            honors_programs.append("WISE")
        if match(r"university\sscholars", txt, re.IGNORECASE):
            honors_programs.append("University Scholars")

        if not honors_programs:
            print(f"{course_number}: Unknown Honors Program: {txt}")

        return {"type": "honors", "value": honors_programs}

    # if there is an "or" | SAME CODE AS "AND"
    if match(r"\sor\s", txt, re.IGNORECASE):
        split_txt = re.split(r"\sor\s", txt)

        # if first txt in split_txt is a course
        if match(FULL_COURSE_NUMBER_REGEX, split_txt[0]):

            for i, t in enumerate(split_txt):
                # if t does not have department code, then add it from the previous element
                if match(r"^(?:(?![a-zA-Z]{3}).)*$", t):
                    split_txt[i] = f"{match(r'[a-zA-Z]{3}', split_txt[i - 1])[0]} {t}"

        if not ignore_non_courses:
            return {
                "type": "or",
                "value": [req_match(t, course_number, ignore_non_courses) for t in split_txt]
            }

        # if non-courses are ignored, then we must remove all the Nones present
        values = list(filter(lambda x: x is not None, [req_match(t, course_number, "whatisthis_or", ignore_non_courses) for t in split_txt]))

        instance = Or_(values, parent_id)
        return instance.full_id(instance.base_id)

    # if txt is a course
    if match(r"^[a-zA-Z]{3}\s\d{3}$", txt):
        return txt

    try:
        raise UnknownRequisite(txt, course_number)
    except UnknownRequisite as e:
        e.log()
        if ignore_non_courses: return None
        return {"type": "custom", "value": txt}


def parse_course(course_node, reqs_ignore_non_courses: bool = False):
    """Parses course information from a webpage and returns a dictionary containing various details about the course.

    Parameters
    ----------
    course_node
        It is a BeautifulSoup object representing a single course
    parse_simple_reqs : bool, optional
        A boolean value that indicates whether the function should simply parse reqs. The default value is False.
    reqs_ignore_non_courses : bool, optional
        A boolean value that indicates whether or not to ignore prequisites that are not other courses

    Returns
    -------
    dict
        A dictionary containing various details about the course. The dictionary contains the following keys:
        - "department": the three-letter department code of the course (e.g. "CSE")
        - "number": the three-digit course number (e.g. "101")
        - "full_course_number": the three-letter department code followed by the three-digit course number (e.g. "CSE 101")
        - "title": the name of the course (e.g. "Introduction to Computer Science")
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
        "title": None,
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
        text = unicodedata.normalize("NFKD", re.sub(
            r"\s{2,}", " ", line.text.replace("\n", " ")).strip())

        # if line is an empty line or is an empty element (of class "clear"), continue to next line
        if not text or (isinstance(line, Tag) and line.attrs.get("class") == ["clear"]):
            continue

        # if line is first (then it specifies the headers)
        if lineI == 1:
            (course_data["department"], course_data["number"], course_data["title"]) = match(
                r"^([a-zA-Z]{3})\s(\d{3}):\s*(.*)$", text)
            course_data["full_course_number"] = course_data["department"] + \
                " " + course_data["number"]

        # if line is second (then it specifies the description)
        elif lineI == 3:
            course_data["description"] = text

        # if line matches DEC
        elif match(r"DEC:", text):
            continue

        # if line matches a DEC or a ,
        elif match(r"^[A-Z,]$", text):
            continue

        # if line matches SBC
        elif match(r"SBC:", text):
            # matches all SBCs if any
            sbcs = re.findall(r"SBC:\s*([A-Z]+(?:,\s*[A-Z]+)*)", text)
            course_data["sbcs"] = sbcs or []

        # if line matches partial fulfillment of SBCs
        elif match(r"Partially fulfills", text):
            continue

        # if line is an SBC
        elif isinstance(line, Tag) and line.name == "a" and line.has_attr("title"):
            course_data["sbcs"].append(text)

        # if line matches credits
        elif match(r"(\d+(?:-\d+)?)\scredits?", text):
            course_data["credits"] = match(
                r"(\d+(?:-\d+)?)\scredits?", text)[0]

        # if line matches requisite
        elif match(r"requisite", text):
            try:
                (req_type, req_text) = match(r"(.*)requisite\(?s?\)?:\s*(.*)$", text, re.IGNORECASE)

                # clean up requisite_type
                req_type = re.sub(r"\s+", " ", req_type.replace("-", " ").lower().strip())

                requisite_obj = req_match(req_text,
                                          course_data['full_course_number'],
                                          course_data["full_course_number"],
                                          reqs_ignore_non_courses)

                # TODO: get smarter parsing here
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
                    print(f"{course_data['full_course_number']}: \"{req_type}\" is not a valid requisite type")

            # if unable to match requisite or if something goes wrong ...
            except:
              try:
                raise UnmatchedCourseLine(text, course_data['full_course_number'])
              except UnmatchedCourseLine as e:
                e.log()

        # otherwise (if line doesn't match) ...
        else:
            try:
                raise UnmatchedCourseLine(text, course_data['full_course_number'])
            except UnmatchedCourseLine as e:
                e.log()

    return course_data


def parse_to_prereq_graph(course_node, data: dict, department_exceptions: List[str]):
    pass
#     course_number = None
#
#     for lineI, line in enumerate(course_node.children):
#         try:
#             # cleans up text by replacing all /n and multiple consecutive spaces with a single space and normalizes unicode
#             text = unicodedata.normalize("NFKD", re.sub(
#                 r"\s{2,}", " ", line.text.replace("\n", " ")).strip())
#
#             # if line is an empty line or is an empty element (of class "clear"), continue to next line
#             if not text or (isinstance(line, Tag) and line.attrs.get("class") == ["clear"]):
#                 continue
#
#             # if line is first (then it specifies the headers)
#             if lineI == 1:
#                 course_number, name = match(
#                     r"^([A-Z]{3}\s\d{3}):\s*(.*)", text)
#
#                 # append the course (to future graph)
#                 data["courses_name_pair"].append([course_number, name])
#
#             # if line matches requisite
#             elif match(r"requisite", text):
#                 assert course_number, "course has not been found!"
#
#                 try:
#                     (req_type, req_text) = match(
#                         r"(.*)requisite\(?s?\)?:\s*(.*)$", text)
#                 except TypeError:
#                     raise UnknownRequisite(text, course_number)
#
#                 # clean up requisite_type
#                 req_type = re.sub(
#                     r"\s+", " ", req_type.replace("-", " ").lower().strip())
#
#                 reqs = simple_req_match(req_text, course_number)
#
#                 if reqs and not match("advisory", req_type) and match("pre", req_type):
#                     for req in reqs:
#                         if req[0:3] not in department_exceptions:
#                             data["prereqs"].append([req, course_number])
#
#         except UnknownRequisite as e:
#             e.log()
