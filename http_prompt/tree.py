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

    def add_path(self, *path):
        name = path[0]
        child = self.find_child(name)
        if not child:
            child = Node(name, parent=self)
            self.children.add(child)

        tail = path[1:]
        if tail:
            child.add_path(*tail)

    def find_child(self, name):
        for child in self.children:
            if child.name == name:
                return child

        # Attempt to match placeholder like /users/{user_id}
        for child in self.children:
            if child.name.startswith('{') and child.name.endswith('}'):
                return child

        return None


class TreeTraveler(object):

    def __init__(self, root):
        self.root = root
        self.cur = root

    def goto(self, path):
        if path.startswith('/'):
            self.cur = self.root
            path = path[1:]

        path = list(filter(lambda s: s, path.split('/')))
        if not path:
            return self.root

        success = True
        cur = self.cur
        for name in path:
            if name == '.':
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
            self.cur = cur
        return success
