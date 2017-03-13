"""Tree data structure for ls command to work with OpenAPI specification."""

from __future__ import unicode_literals


class Node(object):

    def __init__(self, name, data=None, parent=None):
        if name in ('.', '..'):
            raise ValueError("name cannot be '.' or '..'")

        self.name = name
        self.data = data or {}
        self.parent = parent
        self.children = set()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Node('{}', '{}')".format(self.name, self.data.get('type'))

    def __lt__(self, other):
        ta = self.data.get('type')
        tb = other.data.get('type')
        if ta != tb:
            return ta < tb
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name and self.data == other.data

    def __hash__(self):
        return hash((self.name, self.data.get('type')))

    def add_path(self, *path, node_type='dir'):
        name = path[0]
        tail = path[1:]
        child = self.find_child(name, wildcard=False)
        if not child:
            data = {'type': 'dir' if tail else node_type}
            child = Node(name, data=data, parent=self)
            self.children.add(child)

        if tail:
            child.add_path(*tail, node_type=node_type)

    def find_child(self, name, wildcard=True):
        for child in self.children:
            if child.name == name:
                return child

        # Attempt to match wildcard like /users/{user_id}
        if wildcard:
            for child in self.children:
                if child.name.startswith('{') and child.name.endswith('}'):
                    return child

        return None

    def ls(self, *path):
        success = True
        cur = self
        for name in path:
            if not name or name == '.':
                continue
            elif name == '..':
                if cur.parent:
                    cur = cur.parent
            else:
                child = cur.find_child(name)
                if child:
                    cur = child
                else:
                    success = False
                    break
        if success:
            for node in sorted(cur.children):
                yield node
