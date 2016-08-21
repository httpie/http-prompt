import click
from .outputmethod import OutputMethod
from .utils import strip_color_codes


def read_file(path):
    content = None

    with open(path.strip(), 'r') as f:
        content = f.read()
    return content


def put(data, methods=[OutputMethod.echo], path=None):

    if OutputMethod.echo in methods or len(methods) == 0:
        click.echo_via_pager(data)

    if OutputMethod.write_file in methods:
        save_file(data, path, 'w')
    elif OutputMethod.append_file in methods:
        data = '\n' + data
        save_file(data, path, 'a')

def save_file(data, path, file_op='w'):
    data =  strip_color_codes(data)
    with open(path.strip(), file_op) as f:
        f.write(data)
