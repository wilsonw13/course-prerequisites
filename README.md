# Course Prerequisites<!-- omit in toc -->

## Table of Contents<!-- omit in toc -->

- [Description](#description)
- [Design](#design)
  - [Web Scraper](#web-scraper)
    - [Course Details](#course-details)
    - [Requisite Object](#requisite-object)
    - [Graph Representation](#graph-representation)
  - [Query](#query)
  - [Prerequisite Tree Visualizer](#prerequisite-tree-visualizer)
- [Implementation](#implementation)
  - [Course Attribute Parsing](#course-attribute-parsing)
  - [Requisite Parsing](#requisite-parsing)
  - [Parsing Into Graph Representation](#parsing-into-graph-representation)
- [Future Work](#future-work)
  - [General Parsing](#general-parsing)
  - [Requisite Parsing](#requisite-parsing-1)
  - [Query, Prerequisite Tree Visualizer, and User Interface](#query-prerequisite-tree-visualizer-and-user-interface)
  - [Other](#other)
- [Local Installation](#local-installation)
  - [Setting Up Python, Virtual Environment, and Dependencies](#setting-up-python-virtual-environment-and-dependencies)
  - [Scraping](#scraping)
  - [View Visualization](#view-visualization)
- [References](#references)

## Description

This project was created in order to analyze course prerequisites from the Stony Brook Undergraduate Course Bulletin (e.g. [CSE Page](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/cse/courses.php)) by web scraping the page and creating a knowledge base of all courses within the department. The knowledge base is then used to construct a prerequisite tree in order to visualize it using software.

## Design

The application is split into three parts: the web scraper, the query, the prerequisite tree visualizer.

### Web Scraper

The web scraper is written in Python 3.11 and uses the [BeautifulSoup library](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse the contents of the course bulletin. There are two main functions: one that returns an object with all the course details and another that returns a graph representation of the prerequisite tree.

#### Course Details

The object of course details is represented in the following form: 

```ts
{
    "<course_number>": {
        "department": string,
        "number": string,
        "name": string,
        "description": string,
        "prerequisites": {} | null,
        "corequisites": {} | null,
        "antirequisites": {} | null,
        "advisoryPrerequisites": {} | null,
        "advisoryCorequisites": {} | null,
        "sbcs": string[],
        "credits": string
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

- `and`: a logical AND
  - a list of nodes
- `or`: a logical OR
  - a list of nodes
- `course`: a course
  - a string in the form of `DEPARTMENT COURSE_NUMBER` (e.g. `"CSE 214"`)
- `major`: a major
  - a list of strings in the form of `DEPARTMENT` (e.g. `"PSY"`, `"CSE"`, `"AMS"`)
- `standing`: the minimum standing (U1 - U4)
  - an integer ranging `1` - `4`
- `math placement`: the minimum math placement exam score
  - an integer ranging `1` - `9`
- `honors`: the honors colleges (currently only CEAS honors programs are implemented)
  - a list of strings representing the honors programs (e.g. `"WISE"`, `"Honors College"`)
- `custom`: a string that could not be matched (with the parsing rules)
  - a string (e.g. `"co-requisite CSE 260"`, `"permission of instructor"`)

#### Graph Representation

The graph representation of the prerequisite tree is represented in the following form:

```ts
{
    "nodes": [
        {
            "id": string,
            "name": string,
            "group": number
        },
        {
            "id": string,
            "name": string,
            "group": number
        },
    ],
    "links": [
        {
            "source": string,
            "target": string,
        },
        {
            "source": string,
            "target": string,
        },
    ]
}
```

Each node within the `nodes` list has an `id`, `name`, and `group` key and represents a course.
- `id`: course number (e.g. `"CSE 214"`).
- `name`: course name (e.g. `"Data Structures"`).
- `group`: department index which is assigned when parsing the HTML (e.g. `1`, `15`, `63`). This is used to color the nodes.


> Note: These `nodes` are not the same as the nodes in the requisite object. The `nodes` in this graph representation represent courses and the `nodes` in the requisite object represent requisites.

Each link within the `links` list has a `source` and `target` key and represents a prerequisite link.
- `source`: course number of the prerequisite.
- `target`: course number of the course.

> Note: This graph is a simple representation of the prerequisite tree which only contains courses. It does not express the AND/OR relationship between requisites. (i.e. a link between two course nodes means that the source course is mentioned in the target course's prerequisite string)

### Query

The query is also written in Python 3.11 and it reduces the size of the resulting graph by returning a subgraph of the prerequisite tree based off several queries (e.g. a list of course names, departments, transitive prerequisites, etc.).

Currently, the query "function" (found in src/main.py) has the following arguments:

- `courses`: a list of course names (e.g. `["CSE 214", "CSE 220"]`)
- `departments`: a list of departments (e.g. `["CSE", "AMS"]`)
- `show_direct_prerequisites`: a boolean that determines whether or not to show the direct prerequisites of the filtered courses
- `show_transitive_prerequisites`: a boolean that determines whether or not to show all prerequisites of the filtered courses (recursively)
- `show_disconnected_courses`: a boolean that determines whether or not to show courses that disconnected from all other nodes (i.e. the course has no prerequisites and is not a prerequisite to any of the filtered courses)

### Prerequisite Tree Visualizer

The prerequisite tree visualizer is written in JavaScript and uses a [2D/3D force graph library](https://github.com/vasturiano/3d-force-graph) that is built off [ThreeJS](https://github.com/mrdoob/three.js/) rendering to display the resulting graph (after querying).

## Implementation

### Course Attribute Parsing

The web scraper extracts all the `course` elements from the [Stony Brook University Bulletin](https://www.stonybrook.edu/sb/bulletin/current/courses/). Each course is then parsed line by line for the attributes (e.g. course number, name, description) and aggregated into a object which is appended to a dictionary of courses representing the department.

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

*Note: These rules are not perfect and may not match all requisites. They have been initially designed to match most requisites from the CSE page so they may not work for other departments who write their requisites differently. This problem is further discussed in the [Future Work](#future-work) section.*

### Parsing Into Graph Representation

Currently, the graph representation does not use the requisite parsing rules to parse the requisites. Instead, for each course, it adds itself as a node and simply extracts every course from the prerequisite string and creates a link from these courses. 

After all the course prerequisites have been parsed, there may be several `source` courses within links that do not exist as a node within the `nodes` list. The only reason this occurs is if a course is not listed in the bulletin. This is a problem because the graph representation is incomplete and thus the prerequisite tree visualizer will not be able to display the graph.

There are two (or three) possible ways to solve this problem:
1. Add the missing courses as nodes to the `nodes` list.
    - i.e. add all missing courses
2. Remove the links that have a `source` that does not exist as a node within the `nodes` list.
    - i.e. remove all links that contain a missing course
3. *?!! Request that all courses on the bulletin be updated.*

The current implementation uses the first solution and adds the missing courses as nodes to the `nodes` list. However in the future, there will be an option to toggle between the first and second solution and this may become a query option.

## Future Work

### General Parsing

- Some departments do not show their courses on the undergraduate bulletin but rather have their own site to display them.
  - 

### Requisite Parsing

- Find a better or more efficient way to represent prequisites as an object/list.
- Add more nodes to the requisite object (e.g. `permission of instructor`, `department consent`).
- Implemented nested requisites.
  - e.g. [PHY 134](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/phy/courses.php#134): `PHY 126 and PHY 127; or PHY 132; or corequisite PHY 142`
- Build an course equivalency knowledge base (e.g. `AMS 210` is equivalent to `MAT 211`, Math Placement Score of `5` is equivalent to `MAT 131 or AMS 151`). Also applies to AP and IB scores.
- Create a "strict" language for writing requisites unambiguously that can easily parsed and analyzed (e.g. `CSE 214 and (CSE 220 or CSE 260) and (CSE 215 or CSE 230)).
  - e.g. [PHY 311](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/phy/courses.php#311): `PHY 122/124 or PHY 126 and PHY 127 and PHY 134 or PHY 132/134 or PHY 142/134`

### Query, Prerequisite Tree Visualizer, and User Interface

- **(IMPORTANT)** Connect the Python query to the web interface by setting up a Python backend server that either manages a REST API or connects via a websocket.
- Add more query options (e.g. SBCs, credits, depth of prerequisite transitivity).
- Add customizability to the prerequisite tree visualizer (e.g. toggle between 2D/3D, toggle between different graph layouts, toggle between different color schemes).
- Add the ability to make small dynamic changes to the graph (e.g. add/remove nodes, change node color, change node size, change link color, change link width).
- View information about each course on hover (e.g. course number, name, description).

### Other

- Generate course progression in order to complete a major/minor or a set of courses based off prior courses taken.
  - Show an animaton of which courses to take each semester
- Scrape schedule builder, course evaluations, rate my professor, etc. and integrate it into the application to create a more complete course planning tool.

## Local Installation

### Setting Up Python, Virtual Environment, and Dependencies

Ensure you have [Python 3.11](https://www.python.org/downloads/) installed for the best results. After cloning the repository, run the following commands to set up a virtual environment and install the required dependencies:

```bash
python -m venv venv
venv/bin/activate
pip install -r requirements.txt
```

### Scraping

> Note: Currently, you will have to edit the `src/main.py` file in order to execute the various functions with different arguments.

To scrape course data and return all information, run the `full_parse function` in `/src/main.py`

To scrape course data and generate a graph, run the `generate_3d_visualization_json` function in `/src/main.py`

To query the graph, run the query_prerequisite_graph function with optional arguments in `/src/main.py`

### View Visualization

To view the visualization, open either the [2D](/visualizations/2d-force-graph/index.html) or [3D](/visualizations/3d-force-graph/index.html) visualization in a browser.

## References

- [Georgia Tech course tree visualizer](https://devarsi-rawal.github.io/gt-course-tree/)
- (Paper) [The curriculum prerequisite network: a tool for visualizing and analyzing academic curricula](https://arxiv.org/ftp/arxiv/papers/1408/1408.5340.pdf)
- (Paper) [Visualization UW Course Prerequisites Sequences](http://cse512-16s.github.io/fp-dbabbs-jordanstarkey95/paper-dbabbs-jds56.pdf)
- [Rhumbl: Mapping the cirriculum of MIT through OCW](https://rhumbl.com/examples/curriculum-maps)