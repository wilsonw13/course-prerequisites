from file_utils import get_datasets_json, write_to_datasets_json

graph_data = get_datasets_json("full_graph_data.json")

courses_name_pair = [[node["course_number"], node["name"]]
                     for node in graph_data["nodes"]]
prereqs = [[link["source"], link["target"]]
           for link in graph_data["links"]]

write_to_datasets_json("simple_graph_data.json", {
    "courses_name_pair": courses_name_pair,
    "prereqs": prereqs
})
