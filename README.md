# Course Prerequisites

## Description

This project was created in order to analyze course prerequisites from the Stony Brook Undergraduate Course Bulletin (e.g. [CSE Page](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/cse/courses.php)) by web scraping the page and creating a knowledge base of all courses within the department. The knowledge base is then used to construct a prerequisite tree in order to visualize it using software.

## Design

The application is split into three parts: the web scraper, the query function, the prerequisite tree visualizer.

### Web Scraper

The web scraper is written in Python 3.11 and uses the [BeautifulSoup library](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse the contents of the course bulletin. There are two main functions: one that returns an object with all the course details and another that returns a graph representation of the prerequisite tree.

#### Course Details

The object of course details is represented in the following form: 

```json
{
    "<course_number>": {
        "department": "...",
        "number": "...",
        "name": "...",
        "description": "...",
        "prerequisites": {...} | null,
        "corequisites": {...} | null,
        "antirequisites": {...} | null,
        "advisoryPrerequisites": {...} | null,
        "advisoryCorequisites": {...} | null,
        "sbcs": [...],
        "credits": "..."
    },
    ...
}
```

#### Requisite Object

Each requisite object (e.g. prerequisites, corequisites, antirequisites) represents a tree of AND/OR nodes, courses, majors, standing, etc., where each node is an object with a `type` and a `value` key.

Sample Object ([CSE 220](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/cse/courses.php#220)): 

```json
{
    "type": "and",
    "value": [
        {
            "type": "or",
            "value": [
                {
                    "type": "course",
                    "value": "CSE 214"
                },
                {
                    "type": "custom",
                    "value": "co-requisite CSE 260"
                }
            ]
        },
        {
            "type": "major",
            "value": [
                "CSE"
            ]
        }
    ]
}
```

Currently, the following nodes have been implemented:

- `and`: represents a logical AND
  - value: a list of nodes
- `or`: represents a logical OR
  - value: a list of nodes
- `course`: represents a course
  - value: a string in the form of `DEPARTMENT COURSE_NUMBER` (e.g. `"CSE 214"`)
- `major`: represents a major
  - value: a list of strings in the form of `DEPARTMENT` (e.g. `"PSY"`, `"CSE"`, `"AMS"`)
- `standing`: represents the minimum standing (U1 - U4)
  - value: an integer ranging `1` - `4`
- `math placement`: represents the minimum math placement exam score
  - value: an integer ranging `1` - `9`
- `honors`: represents the honors colleges (currently only CEAS honors programs are implemented)
  - value: a list of strings representing the honors programs (e.g. `"WISE"`, `"Honors College"`)
- `custom`: represents a string that could not be matched (with the parsing rules)
  - value: a string (e.g. `"co-requisite CSE 260"`, `"permission of instructor"`)

#### Graph Representation

The graph representation of the prerequisite tree is represented in the following form:

```json
{
    "nodes": [
        {
            "id": "...",
            "group": "..."
        },
        {
            "id": "...",
            "group": "..."
        },
        ...
    ],
    "links": [
        {
            "source": "...",
            "target": "...",
        },
        {
            "source": "...",
            "target": "...",
        },
        ...
    ]
}
```

### Query Function

The query function is also written in Python 3.11 and it reduces the size of the resulting graph by returning a subgraph of the prerequisite tree based off several queries (e.g. a list of course names, departments, transitive prerequisites, etc.).

Currently, the query function (found in src/main.py) has the following arguments:

- `courses`: a list of course names (e.g. `["CSE 214", "CSE 220"]`)
- `departments`: a list of departments (e.g. `["CSE", "AMS"]`)
- `show_direct_prerequisites`: a boolean that determines whether or not to show the direct prerequisites of the filtered courses
- `show_transitive_prerequisites`: a boolean that determines whether or not to show all prerequisites of the filtered courses (recursively)
- `show_disconnected_courses`: a boolean that determines whether or not to show courses that disconnected from any other node (i.e. the course has no prerequisites and is not a prerequisites to any of the filtered courses)

### Prerequisite Tree Visualizer

The prerequisite tree visualizer is written in JavaScript and uses a [2D/3D force graph library](https://github.com/vasturiano/3d-force-graph) that is built off [ThreeJS](https://github.com/mrdoob/three.js/) rendering to display the resulting graph (after querying).

## Implementation

### Requisite Parsing

The web scraper uses a set of rules, similar to that of context free grammar (CFG), to parse the course requisites. The rules are as follows (in order of precedence):
- `and` matches all `and` or `;` and recursively parses each side
- `major` matches `major` and returns a list of majors
- `standing` matches `standing` and returns the corresponding integer
- `math placement` matches `math placement exam` and returns the corresponding integer
- `honors` matches the words `honors` or `university scholars` and returns a list of honors programs
- `or` matches all `or` and recursively parses each side
- `course` matches a course in the form of `DEPARTMENT COURSE_NUMBER` (e.g. `"CSE 214"`) and returns it
- `custom` matches any string that could not be matched by the previous rules and returns it

*Note: These rules are not perfect and may not match all requisites. They have been initially designed to match the requisites.
For example, the rule for `course` will not match courses that are not in the form of `DEPARTMENT COURSE_NUMBER` (e.g. `"CSE 214H"`, `"CSE 214/215"`, `"CSE 214 or 215"`, etc.).*



## References

- [Georgia Tech course tree visualizer](https://devarsi-rawal.github.io/gt-course-tree/)
- (Paper) [The curriculum prerequisite network: a tool for visualizing and analyzing academic curricula](https://arxiv.org/ftp/arxiv/papers/1408/1408.5340.pdf)
- (Paper) [Visualization UW Course Prerequisites Sequences](http://cse512-16s.github.io/fp-dbabbs-jordanstarkey95/paper-dbabbs-jds56.pdf)
- [Rhumbl: Mapping the cirriculum of MIT through OCW](https://rhumbl.com/examples/curriculum-maps)