from file_utils import get_from_json_dir, write_to_json_dir

graph_data = get_from_json_dir("full_graph_data.json")

courses_name_pair = [[node["course_number"], node["name"]]
                     for node in graph_data["nodes"]]
prereqs = [[link["source"], link["target"]]
           for link in graph_data["links"]]

write_to_json_dir("simple_graph_data.json", {
    "courses_name_pair": courses_name_pair,
    "prereqs": prereqs
})
