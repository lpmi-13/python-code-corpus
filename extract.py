from pymongo import MongoClient
import json

client = MongoClient()
db = client.ast

result_dict = {
  "fors": [],
  "ifs": [],
  "lists": [],
  "listcomps": [],
  "dicts": [],
  "dictcomps": [],
  "functions": [],
}

def output_json(handle):
    results = handle.find(
        {}, {'_id': False }
    ).limit(25)

    for result in results:
        result_dict[result['type']].append(json.dumps(result))


output_json(db.fors)
output_json(db.ifs)
output_json(db.lists)
output_json(db.listcomps)
output_json(db.dicts)
output_json(db.dictcomps)
output_json(db.functions)

with open('results.json', 'a') as output_file:
    output_file.write(json.dumps(result_dict))
