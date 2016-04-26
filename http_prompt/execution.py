from urlparse import urljoin

from httpie.core import main as httpie_main
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mutation+ / nonconcat_mutation
    immutation = preview / action

    concat_mutation = header_mutation / querystring_mutation / body_mutation /
                      option_mutation
    nonconcat_mutation = cd / su / "reset"
    preview = _ tool _ action
    action = _ method _ concat_mutation*

    header_mutation = _ varname ":" string _
    querystring_mutation = _ varname "==" string _
    body_mutation = _ string "=" string _
    option_mutation = _ "--" varname _
    cd = _ "cd" _ string _
    su = _ "su" _ string _
    tool = "httpie" / "curl"
    method = "get" / "post" / "put" / "delete" / "patch"

    varname = ~r"[^\s:;=]+"
    string = ~r"'.*'" / ~r"[^ ]+"
    _ = ~r"\s*"
""")


class ExecutionVisitor(NodeVisitor):

    def __init__(self, context):
        super(ExecutionVisitor, self).__init__()
        self.context = context

    def visit_method(self, node, children):
        httpie_main([node.text] + self.context.to_args())
        return node

    def visit_cd(self, node, children):
        path = children[3].text
        self.context.url = urljoin(self.context.url, path)
        return node

    def generic_visit(self, node, children):
        if len(children) == 1:
            return children[0]

        new_children = []
        for child in node:
            if child.expr_name != '_':
                new_children.append(child)
        node.children = new_children
        return node


def execute(command, context):
    root = grammar.parse(command)
    visitor = ExecutionVisitor(context)
    visitor.visit(root)
