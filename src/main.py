from bs4 import BeautifulSoup, SoupStrainer
import json
from parser import parse_course

with open("../cse.html") as file:
    doc = BeautifulSoup(file, "lxml", parse_only=SoupStrainer(class_="course"))


cse_data = {}

data = parse_course(doc.find(id="102"))

# for node in doc:
#     parse_course(cse_data)

with open("../data.json", "w") as f:
    json.dump(data, f, indent=4)
