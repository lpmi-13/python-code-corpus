import git
import ast
import astor
import os
import sys
from pymongo import MongoClient

GITHUB_FILE_PATH_INTERMEDIATE = '/blob/master/'

client = MongoClient()
db = client.ast

fors = db.fors
ifs = db.ifs
whiles = db.whiles
functions = db.functions
asyncfunctions = db.asyncfunctions
lists = db.lists
listcomps = db.listcomps
dicts = db.dicts
dictcomps = db.dictcomps
sets = db.sets
setcomps = db.setcomps


def convert_code_line(index, contents):
    return {"line_number": index + 1, "line_content": contents}

def extract_and_store(node, mongo_collection, filepath, full_repo_url):

    file_path_in_remote_repo = filepath.split('/')[1:]
    filename = filepath.split('/')[-1]
    # copy it back to what it looks like in the source, conveniently incorporating whitespace
    code = astor.to_source(node)
    split_code = [line for line in code.split('\n') if line is not '']

    # this is ugly, but the quickest way to get the file contents by line, which we need for the direct link to the file in github
    with open(filepath, 'r') as input_file:
       file_lines = input_file.readlines()
    
    # now stop everything and get the line from the original file
    for ind, x in enumerate(file_lines):
        
        # IT'S A HACKDAY!!!
        # TODO : later, see if there's an easy way to check for the variable
        # being assigned, the equals, and the first char after the equals to
        # be at a particular line in the file, since this approach currently
        # misses assignment like the following that gets split across lines:
        # new_dict = {
        #     "thing1": 3,
        #     "thing2": 2,
        #     "thing3": 1
        # }
        if x.strip().replace('"', '\'') == split_code[0].replace('"', '\''):
            original_file_line = ind + 1
            break

    try:
        mongo_collection.insert_one({"type": "{}".format(mongo_collection.name),
                             "project_source": full_repo_url,
                             "direct_link_to_file_line": full_repo_url + GITHUB_FILE_PATH_INTERMEDIATE + '/'.join(file_path_in_remote_repo) + '#L{}'.format(original_file_line),
                             "contents": {
                               "total_lines": len(split_code),
                               "lines": [convert_code_line(ind,x) for ind, x in enumerate(split_code)] }})
        print('inserting {} from {}...'.format(mongo_collection.name, filepath))
        print('\n')

    except:
        print('skipping this one, for reasons...')

def grab_examples(full_repo_url, filepath):
    """
    we grab the contents of each file and parse it, then walk it
    """
    with open(filepath, 'r') as source:
        file_contents = source.read()

    try:
        tree = ast.parse(file_contents)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                extract_and_store(node, functions, filepath, full_repo_url)
            if isinstance(node, ast.AsyncFunctionDef):
                extract_and_store(node, asyncfunctions, filepath, full_repo_url)
            if isinstance(node, ast.If):
                extract_and_store(node, ifs, filepath, full_repo_url)
            if isinstance(node, ast.While):
                extract_and_store(node, whiles, filepath, full_repo_url)
            if isinstance(node, ast.For):
                extract_and_store(node, fors, filepath, full_repo_url)

            if isinstance(node, ast.Assign):
                # we're filtering out empty list assignment for now
                if isinstance(node.value, ast.List) and node.value.elts != []:
                    extract_and_store(node, lists, filepath, full_repo_url)
                if isinstance(node.value, ast.ListComp):
                    extract_and_store(node, listcomps, filepath, full_repo_url)
                # we're filtering out empty dict assignment for now
                if isinstance(node.value, ast.Dict) and node.value.keys != []:
                    extract_and_store(node, dicts, filepath, full_repo_url)
                if isinstance(node.value, ast.DictComp):
                    extract_and_store(node, dictcomps, filepath, full_repo_url)
                if isinstance(node.value, ast.Set):
                    extract_and_store(node, sets, filepath, full_repo_url)
                if isinstance(node.value, ast.SetComp):
                    extract_and_store(node, setcomps, filepath, full_repo_url)
    except:
        print('ast parse error, skip this one')

with open('url_list.txt', 'r') as input_file:
    urls = input_file.readlines()

for url in urls:
    url = url.strip()
    local_dir_name = url.split('/')[-1]

    print('cloning {}...'.format(url))
    
    try:
        git.Git('./').clone(url)
    except:
        print('directory already exists...skipping...')

    for path, subdirs, files in os.walk(local_dir_name):
        for name in files:
            if name.endswith('.py'):
                grab_examples(url, os.path.join(path, name))
