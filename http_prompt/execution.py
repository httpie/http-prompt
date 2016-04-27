import click

from urlparse import urljoin

from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

from .context import Context


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mutation+ / nonconcat_mutation
    immutation = preview / action

    concat_mutation = header_mutation / querystring_mutation / body_mutation /
                      option_mutation
    nonconcat_mutation = cd / "reset"
    preview = _ tool _ (method _)? concat_mutation*
    action = _ method _ concat_mutation*

    header_mutation = _ varname ":" string _
    querystring_mutation = _ varname "==" string _
    body_mutation = _ varname "=" string _
    option_mutation = _ "--" varname _
    cd = _ "cd" _ string _
    tool = "httpie" / "curl"
    method = "get" / "post" / "put" / "delete" / "patch"

    varname = ~r"[^\s:;=]+"
    string = ~r"'.*'" / ~r"[^ ]+"
    _ = ~r"\s*"
""")


def urljoin2(base, path, **kwargs):
    if not base.endswith('/'):
        base += '/'
    url = urljoin(base, path)
    if url.endswith('/'):
        url = url[:-1]
    return url


class ExecutionVisitor(NodeVisitor):

    def __init__(self, context):
        super(ExecutionVisitor, self).__init__()
        self.context = context

        self.context_override = Context(context.url)
        self.method = None
        self.tool = None

    def visit_method(self, node, children):
        self.method = node.text
        return node

    def visit_cd(self, node, children):
        path = children[3].text
        self.context_override.url = urljoin2(self.context_override.url, path)
        return node

    def visit_header_mutation(self, node, children):
        return self._visit_key_value_mutation(
            node, children, self.context_override.headers)

    def visit_querystring_mutation(self, node, children):
        return self._visit_key_value_mutation(
            node, children, self.context_override.querystring_params)

    def visit_body_mutation(self, node, children):
        return self._visit_key_value_mutation(
            node, children, self.context_override.body_params)

    def _visit_key_value_mutation(self, node, children, dst_dict):
        key = children[1].text
        value = children[3].text
        dst_dict[key] = value
        return node

    def visit_option_mutation(self, node, children):
        if node.text not in self.context_override.options:
            self.context_override.options.append(node.text)
        return node

    def visit_tool(self, node, children):
        self.tool = node.text
        return node

    def visit_mutation(self, node, children):
        self.context.update(self.context_override)
        return node

    def _final_context(self):
        context = self.context.copy()
        context.update(self.context_override)
        return context

    def visit_immutation(self, node, children):
        context = self._final_context()

        if children[0].expr_name == 'preview':
            command = [self.tool]
            if self.tool == 'httpie':
                command += context.httpie_args(self.method)
            else:
                assert self.tool == 'curl'
                command += context.curl_args(self.method)
            click.echo(' '.join(command))
        else:
            assert children[0].expr_name == 'action'
            httpie_main(context.httpie_args())

    def generic_visit(self, node, children):
        return node


def execute(command, context):
    try:
        root = grammar.parse(command)
    except ParseError:
        click.echo('Invalid command')
    else:
        visitor = ExecutionVisitor(context)
        visitor.visit(root)
