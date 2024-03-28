from file_utils import get_from_json_dir

courses = get_from_json_dir("data/all_courses_full.json")

def translate_to_prolog(node):
    if node["type"] == "and":
        return ", ".join(f"({translate_to_prolog(child)})" for child in node["value"])
    elif node["type"] == "or":
        return "; ".join(f"({translate_to_prolog(child)})" for child in node["value"])
    elif node["type"] == "course":
        return node["value"].replace(" ", "")


with open("./rules.txt", "a", encoding="utf-8") as f:
    for course, data in courses.items():
        reqs = data["prerequisites"]

        if reqs:
            f.write(f"{course.replace(' ', '')} :- {translate_to_prolog(reqs)}.\n")