import click
import json
from .utils import is_json
from .outputmethod import OutputMethod

def put(data, methods=[OutputMethod.echo], path=None):
    is_json_data = is_json(data)
    json_indent = 4

    if OutputMethod.echo in methods:
        if is_json_data:
            click.echo_via_pager(json.dump(data, json_indent, sort_keys=True))
        else:
            click.echo_via_pager(data)


    if OutputMethod.write_file in methods:
        save_file(data, path, 'w', is_json_data, json_indent)
    elif OutputMethod.append_file in methods:
        data += '\n'
        save_file(data, path, 'a', is_json_data, json_indent)

def save_file(data, path, file_op, is_json_data, json_indent):
    with open(path.strip(), file_op) as f:
        if is_json_data:
            json.dump(data, f, json_indent)
        else:
            f.write(data)

