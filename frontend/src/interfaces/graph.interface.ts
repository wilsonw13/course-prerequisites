export interface Node {
    course_number: string;
    name: string;
    group: number;
}

export interface Link {
    source: string;
    target: string;
}

export interface GraphData {
    nodes: Node[];
    links: Link[];
}
