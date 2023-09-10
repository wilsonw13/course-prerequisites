from typing import List, Set
import argparse

from file_utils import get_from_json_dir

ALL_COURSES_ATTRS = get_from_json_dir("data/all_courses.json")
ALL_COURSES = set(ALL_COURSES_ATTRS.keys())
ALL_PREREQS = get_from_json_dir("data/all_prereqs.json")

courses: Set[str] = set()

# Queries


def department(departments: List[str]):
    """Returns all courses in the given departments"""
    return {course_num for course_num, course_attrs in ALL_COURSES_ATTRS.items() if course_attrs["department"] in departments}


def course(courses: List[str]):
    """Returns all courses in the given list"""
    return {c for c in courses if c in ALL_COURSES_ATTRS}


def level(number: int):
    """Returns all courses in the given level or higher"""
    return {course_num for course_num, course_attrs in ALL_COURSES_ATTRS.items() if int(course_attrs["number"]) >= number}


def prerequisite(depth: int = 100):
    """Returns all prerequisite courses of the main set of the given depth or less (REACHABILITY)"""
    reachable = courses.copy()
    # used to track newly reachable courses (to only recurse on those)
    newly_reachable = reachable.copy()

    while depth > 0 and newly_reachable:
        new = set()

        for course in newly_reachable:
            # only add courses to new if they weren't already in reachable
            new.update(set(ALL_PREREQS.get(course, set()))
                       .difference(reachable))

        reachable.update(new)
        newly_reachable = new
        depth -= 1

    return reachable

# RUNNING


def run_queries(queries):
    for set_op, name, arg in queries:
        queried_courses = globals()[name](arg)

        global courses

        if set_op == "ADD":
            courses.update(queried_courses)
        elif set_op == "REMOVE":
            courses.difference_update(queried_courses)
        elif set_op == "INTERSECT":
            courses.intersection_update(queried_courses)
        elif set_op == "UPDATE":
            courses = queried_courses

    res_courses = courses.copy()
    courses.clear()

    return res_courses


if __name__ == "__main__":
    # Prerequisites of CSE 307
    print("Prerequisites of CSE 307:")
    print(run_queries([("ADD", "course", ["CSE 307"]),
                       ("ADD", "prerequisite", 1),
                       ("REMOVE", "course", ["CSE 307"])]))

    # All AMS prerequisites of CSE 215, CSE 355
    print("All AMS prerequisites of CSE 215, CSE 355:")
    print(run_queries([("ADD", "course", ["CSE 215", "CSE 355"]),
                       ("ADD", "prerequisite", 100),
                       ("INTERSECT", "department", ["AMS"])]))

    # 300 level CSE courses
    print("300 level CSE courses:")
    print(run_queries([("ADD", "department", ["CSE"]),
                       ("INTERSECT", "level", 300)]))
