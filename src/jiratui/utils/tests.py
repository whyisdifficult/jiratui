import json
import os
import re


def load_json_response(current_file: str, filename: str):
    """Loads JSON file."""
    base_dir = os.path.dirname(current_file)
    file_path = os.path.join(base_dir, 'responses', filename)
    with open(file_path) as json_file:
        return json.load(json_file)


def get_url_pattern(s):
    """Returns a non-greedy regexp for a passed string"""
    return re.compile(f'.*{s}.*')
