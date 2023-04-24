from bs4 import BeautifulSoup, SoupStrainer
import os
import json
from parser import parse_course

with open("../cse.html") as file:
    doc = BeautifulSoup(file, "lxml", parse_only=SoupStrainer(class_="course"))


cse_data = {}

data = parse_course(doc.find(id="320"))

# for node in doc:
#     parse_course(cse_data)

# creates logs directory if it doesn't exist
os.makedirs(os.path.dirname("../logs/"), exist_ok=True)

# writes to the directory
with open("../logs/data.json", "w") as f:
    json.dump(data, f, indent=4)
