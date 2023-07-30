# Documentation<!-- omit in toc -->

## Table of Contents<!-- omit in toc -->

- [Description](#description)
- [Design](#design)
  - [Web Scraper](#web-scraper)
  - [Query Function](#query-function)
  - [Prerequisite Tree Visualizer](#prerequisite-tree-visualizer)
  - [Websocket Server](#websocket-server)
- [Implementation](#implementation)
  - [Web Scraper](#web-scraper-1)
    - [Parsing Specifics](#parsing-specifics)
  - [Query Function](#query-function-1)
    - [Graph Representation](#graph-representation)
  - [Prerequisite Tree Visualizer](#prerequisite-tree-visualizer-1)
  - [Websocket Server](#websocket-server-1)
- [Future Work](#future-work)
  - [General Parsing](#general-parsing)
  - [Requisite Parsing](#requisite-parsing)
  - [Query, Prerequisite Tree Visualizer, and User Interface](#query-prerequisite-tree-visualizer-and-user-interface)
  - [Other](#other)
- [Local Installation](#local-installation)
- [References](#references)

## Description

This project was created in order to analyze course prerequisites from the Stony Brook Undergraduate Course Bulletin (e.g. [CSE Page](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/cse/courses.php)) by web scraping the page and creating a knowledge base of all courses within the department. The knowledge base is then used to construct a prerequisite tree in order to visualize it using software. It can also be queried to return a subgraph of the prerequisite tree based off several queries (e.g. a list of course names, departments, transitive prerequisites).

## Design

![Design](/docs/images/design.png)

The application consists of four main parts: the web scraper, the query function, the web client (prerequisite tree visualizer), and the websocket server.

### Web Scraper

The web scraper scrapes the Stony Brook course bulletin and parses the course attributes and requisites into a knowledge base which is then stored, in this case, as a [JSON file](/backend/json/full_graph.json). Ideally, the web scraper would be run periodically to update the knowledge base with any changes to the course bulletin (e.g. after each semester).

### Query Function

The query function requires the whole knowledge base (i.e. [full_graph.json](/backend/json/full_graph.json)) and a query object whose keys are the query options and whose values are the query arguments. The query function then returns a list of courses which, along with their requisites (retrieved from the knowledge base), is used to construct a graph representation of the prerequisite tree (i.e. a subgraph of the full graph).

### Prerequisite Tree Visualizer

The prerequisite tree visualizer is a web client that displays the graph representation of the prerequisite tree that is built off a 3D force graph library. This web client allows the user to query the graph and view the resulting subgraph.

On startup, the prerequisite tree visualizer connects to the websocket server and receives all query options, a list of all the possible queries that can be made. The user can then select a query and enter the query arguments. Once the query is submitted by the user, it is then sent to the websocket server which returns the resulting subgraph and displays it to the user.

### Websocket Server

The websocket server facilitates communication between the backend server and any number of frontend web clients. It maintains a persistent connection with each client and manages the sending and receiving of incoming messages, which in this case are queries and graph data.

Whenever a client connects to the websocket server, the server sends the client a list of all the possible queries that can be made. Afterwards, the client can send a query request to the server which will then be processed by the query function. The resulting subgraph is then sent back to the client.



## Implementation

### Web Scraper

The web scraper is written in Python and uses the [BeautifulSoup library](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to parse the contents of the [Stony Brook University Undergraduate course bulletin](https://www.stonybrook.edu/sb/bulletin/current/) across every department (e.g. [CHE](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/che/courses.php), [CSE](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/cse/courses.php), [AMS](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/ams/courses.php), [MAT](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/mat/courses.php)).

After parsing all the courses and prerequisites, all the "extraneous" prerequisite relationships are removed. These removed prerequisite relationships have source courses that are not listed in the bulletin and thus are not included in the graph representation. This is done to ensure that the graph representation is complete and that the prerequisite tree visualizer can display the graph.

#### Parsing Specifics

The web scraper extracts all the `course` elements from the UG bulletin, looping for each department. Each course is then parsed line by line for the attributes (e.g. course number, name, prerequisites). Each prerequisite string in each course is extracted for each course it contains, however in the [future](#future-work), an prerequisite object with nested relationships (i.e. AND/OR) will be used instead.

Each course and name pair is appended to a course list and each prerequisite pair (source, target) is appended to a prerequisite list with each list being a value within dictionary. After all the departments and courses have finished parsing, the course list and prerequisite list are written to a JSON file:

```json
{
  "courses_name_pair": [
    [
      "AAS 102",
      "Eastern Religions"
    ],
    [
      "AAS 110",
      "Appreciating Indian Music"
    ],
  ],
  "prereqs": [
    [
        "ANT 102",
        "AAS 372"
    ],
    [
        "KOR 212",
        "AAS 385"
    ],
  ]
}
```

### Query Function

The query function is also written in Python and it returns a subgraph of the prerequisite tree based off several queries (e.g. a list of course names, departments, transitive prerequisites, etc.). In order to run the transitivity query, the query functions uses [XSB](https://xsb.sourceforge.net/), a logic programming language, with [Alda](https://github.com/DistAlgo/alda), a Python-extended language with distributive algorithms to run the prerequisite transitivity query, thus it has a `.da` file extension.

A [query options](./backend/json/query_options.json) variable specifies a list of query options that the query function can use to filter the graph. The query runs by querying the full graph data based off these specific queries and returns a subgraph.

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

### Prerequisite Tree Visualizer

The prerequisite tree visualizer is written in JavaScript and uses a [3D force graph library](https://github.com/vasturiano/react-force-graph) that is built off [ThreeJS](https://github.com/mrdoob/three.js/) rendering to display the resulting graph (after querying).

### Websocket Server

**Work in Progress**

## Future Work

### General Parsing

- Some departments do not show their courses on the undergraduate bulletin but rather have their own site to display them.

### Requisite Parsing

- Find a better or more efficient way to represent prerequisites as an object/list.
- Implemented nested requisites.
  - e.g. [PHY 134](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/phy/courses.php#134): `PHY 126 and PHY 127; or PHY 132; or corequisite PHY 142`
- Build an course equivalency knowledge base (e.g. `AMS 210` is equivalent to `MAT 211`, Math Placement Score of `5` is equivalent to `MAT 131 or AMS 151`). Also applies to AP and IB scores.
- Create a "strict" language for writing requisites unambiguously that can easily parsed and analyzed (e.g. `CSE 214 and (CSE 220 or CSE 260) and (CSE 215 or CSE 230)).
  - e.g. [PHY 311](https://www.stonybrook.edu/sb/bulletin/current/academicprograms/phy/courses.php#311): `PHY 122/124 or PHY 126 and PHY 127 and PHY 134 or PHY 132/134 or PHY 142/134`

### Query, Prerequisite Tree Visualizer, and User Interface

- Add more query options (e.g. SBCs, credits, depth of prerequisite transitivity).
- Add customizability to the prerequisite tree visualizer (e.g. toggle between 2D/3D, toggle between different graph layouts, toggle between different color schemes).
- Add the ability to make small dynamic changes to the graph (e.g. add/remove nodes, change node color, change node size, change link color, change link width).
- View information about each course on hover (e.g. course number, name, description).

### Other

- Generate course progression in order to complete a major/minor or a set of courses based off prior courses taken.
  - Show an animaton of which courses to take each semester
- Scrape schedule builder, course evaluations, rate my professor, etc. and integrate it into the application to create a more complete course planning tool.

## Local Installation

See the root [README.md](/README.md#local-installation-on-windows) file for instructions on how to run the application locally.

## References

- [Georgia Tech course tree visualizer](https://devarsi-rawal.github.io/gt-course-tree/)
- (Paper) [The curriculum prerequisite network: a tool for visualizing and analyzing academic curricula](https://arxiv.org/ftp/arxiv/papers/1408/1408.5340.pdf)
- (Paper) [Visualization UW Course Prerequisites Sequences](http://cse512-16s.github.io/fp-dbabbs-jordanstarkey95/paper-dbabbs-jds56.pdf)
- [Rhumbl: Mapping the cirriculum of MIT through OCW](https://rhumbl.com/examples/curriculum-maps)