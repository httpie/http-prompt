import click

from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from six.moves.urllib.parse import urljoin

from .context import Context


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mutation+ / nonconcat_mutation
    immutation = preview / action

    concat_mutation = header_mutation / querystring_mutation / body_mutation /
                      option_mutation
    nonconcat_mutation = cd / rm
    preview = _ tool _ (method _)? concat_mutation*
    action = _ method _ concat_mutation*

    header_mutation = _ varname ":" string _
    querystring_mutation = _ varname "==" string _
    body_mutation = _ varname "=" string _
    option_mutation = long_option / short_option
    long_option = _ "--" long_optname optvalue_assign? _
    short_option = _ "-" short_optname optvalue_assign? _
    cd = _ "cd" _ string _
    rm = _ "rm" _ ~r"\-(h|q|b|o)" _ varname _
    tool = "httpie" / "curl"
    method = "get" / "post" / "put" / "delete" / "patch"

    long_optname = ~r"[a-z\-]+"
    short_optname = ~r"[a-z]"i
    optvalue_assign = ~r"(\s+|=)" optvalue
    optvalue = ~r"[^\-][^\s]+" / ~r"'[^']*'"
    varname = ~r"[a-z0-9_\-\.]+"i
    string = ~r"'[^']*'" / ~r"[^ ]+"
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

    def visit_rm(self, node, children):
        kind = children[3].text
        name = children[5].text
        if kind == '-h':
            target = self.context.headers
        elif kind == '-q':
            target = self.context.querystring_params
        elif kind == '-b':
            target = self.context.body_params
        else:
            assert kind == '-o'
            target = self.context.options
        del target[name]
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
        option = children[0]
        name = option.children[1].text + option.children[2].text
        value = None

        if option.children[3].text.strip():
            value = option.children[3].children[0].children[1].text

        self.context_override.options[name] = value
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
            if self.tool == 'httpie':
                command = ['http'] + context.httpie_args(self.method)
            else:
                assert self.tool == 'curl'
                command = ['curl'] + context.curl_args(self.method)
            click.echo(' '.join(command))
        else:
            assert children[0].expr_name == 'action'
            httpie_main(context.httpie_args(self.method))

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
