import json
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

basic_path_json = "basic_path.json"

def get_basic_path(basic_path_json = basic_path_json):
    with open(basic_path_json) as f:
        basic_path = json.load(f)
    for key in basic_path:
        basic_path[key] = os.path.expanduser(basic_path[key]).encode(encoding='utf-8')

    return basic_path
