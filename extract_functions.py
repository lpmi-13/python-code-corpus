from pymongo import MongoClient
import json
import sys

NUMBERS_OF_LINES = ((3,6), (5,9), (7,12))

try:
    client = MongoClient(host= ['localhost:27017'], serverSelectionTimeoutMS = 2000)
    client.server_info()
    db = client.ast
except:
    print('mongo isn\'t currently running...please start it first')
    sys.exit()

result_dict = {
    "functions": {
        "small": [],
        "medium": [],
        "large": []
    }
}


def output_json_for_project(handle, project_name, upper_bound, lower_bound):
    results = handle.find(
        {'project_source': project_name, 'contents.total_lines': {'$lt': upper_bound, '$gt': lower_bound}},
        {'_id': False}
    ).limit(1)

    for result in results:
        if lower_bound < 4:
            result_dict[result['type']]['small'].append(json.dumps(result))
        elif lower_bound > 6:
             result_dict[result['type']]['large'].append(json.dumps(result))       
        else:
              result_dict[result['type']]['medium'].append(json.dumps(result))                   

def get_all_distinct(handle):
    results = handle.distinct('project_source')
    return results 

all_projects = get_all_distinct(db.functions)

for project in all_projects:

    for lower_bound, upper_bound in NUMBERS_OF_LINES:
        output_json_for_project(db.functions, project, upper_bound, lower_bound)


with open('function-results.json', 'a') as output_file:
    output_file.write(json.dumps(result_dict))
