import re
import unicodedata
from bs4 import Tag

from log import append_to_file

def match (regex, match_text, flags=None):
    """
    :param regex:
    :param match_text:
    :param flags: regex match flags
    :return: The first match found (if using groups) or all matches (if not using groups), otherwise None
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

def requisite_match(txt, data):
    # cleans txt
    txt = txt.strip()
    # if txt is an empty string, return
    if not txt: return

    # removes the "C or higher" from txt
    if match(r"[ABCD][+-]?\sor\shigher(?:\s?in|:)\s*", txt):
        txt = match(r"[ABCD][+-]? or higher(?:\s?in|:)\s*(.*)", txt)[0]

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
            "value": [requisite_match(t, data) for t in or_split_txt]
        }

    # if txt is majors
    if match(r"major", txt, re.IGNORECASE):
        return {"type": "major", "value": [x for x in match(r"([A-Z]{3})", txt)]}

    # if txt is standing
    if match(r"standing", txt, re.IGNORECASE):
        return {"type": "standing", "value": min([int(x) for x in match(r"U(\d+)", txt)])}

    # if txt is math placement exam
    if match(r"math.*placement\sexam", txt, re.IGNORECASE):
        return {"type": "math placement", "value": min([int(x) for x in match(r"level\s(\d+)", txt, re.IGNORECASE)])}

    # if txt is any of the honors programs
    if match(r"(?:honors|university\sscholars)", txt, re.IGNORECASE):
        honors_programs = []

        if match(r"computer\sscience\shonors", txt, re.IGNORECASE): honors_programs.append("CS Honors")
        if match(r"honors\scollege", txt, re.IGNORECASE): honors_programs.append("Honors College")
        if match(r"wise\shonors", txt, re.IGNORECASE): honors_programs.append("WISE Honors")
        if match(r"university\sscholars", txt, re.IGNORECASE): honors_programs.append("University Scholars")

        if not honors_programs: print(f"{data['department']} {data['number']}: Unknown Honors Program: {txt}")

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
            "value": [requisite_match(t, data) for t in or_split_txt]
        }

    # if txt is a course
    if match(r"^[a-zA-Z]{3}\s\d{3}$", txt):
        return {"type": "course", "value": txt}

    append_to_file("unknown-reqs.txt", f"{data['department']} {data['number']}: {txt}")
    return {"type": "custom", "value": txt}

def parse_course(course_node):
    # default data object
    data = {
        "department": None,
        "number": None,
        "name": None,
        "description": None,
        "prerequisites": None,
        "corequisities": None,
        "antirequisites": None,
        "advisoryPrerequisites": None,
        "advisoryCorequisities": None,
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
            (data["department"], data["number"], data["name"]) = match(r"^([a-zA-Z]{3})\s(\d{3}):\s*(.*)$", text)

        # if line is second (then it specifies the description)
        elif lineI == 3:
            data["description"] = text

        # if line matches SBC
        elif match(r"^SBC:", text):
            data["sbcs"] = match(r"^SBC:\s*(.*)", text)[0].split(", ")

        # if line matches credits
        elif match(r"(\d+(?:-\d+)?)\scredits?", text):
            data["credits"] = match(r"(\d+(?:-\d+)?)\scredits?", text)[0]

        # if line matches requisite
        elif match(r"requisite", text):
            (requisite_type, requisites_text) = match(r"(.*)requisites?:\s*(.*)$", text)

            # clean up requisite_type
            requisite_type = re.sub(r"\s+", " ", requisite_type.replace("-", " ").lower().strip())

            requisite_obj = requisite_match(requisites_text, data)

            match requisite_type:
                case "pre":
                    data["prerequisites"] = requisite_obj
                case "co":
                    data["corequisities"] = requisite_obj
                case "pre or co":
                    data["prerequisites"] = data["corequisities"] = requisite_obj
                case "anti":
                    data["antirequisites"] = requisite_obj
                case "advisory pre":
                    data["advisoryPrerequisites"] = requisite_obj
                case "advisory co":
                    data["advisoryCorequisities"] = requisite_obj
                case "advisory pre or co":
                    data["advisoryPrerequisites"] = data["advisoryCorequisities"] = requisite_obj
                case _:
                    print(f"\"{requisite_type}\" is not a valid requisite type")

        # otherwise (if line doesn't match) ...
        else: append_to_file("unmatched.txt", f"{data['department']} {data['number']}: {text}")

    return data
