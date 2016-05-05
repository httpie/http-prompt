import click
import six

from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from six.moves.urllib.parse import urljoin

from .context import Context
from .utils import unescape


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mut+ / nonconcat_mut
    immutation = preview / action

    concat_mut = option_mut / full_quoted_mut / value_quoted_mut / unquoted_mut
    nonconcat_mut = cd / rm
    preview = _ tool _ (method _)? concat_mut*
    action = _ method _ concat_mut*

    unquoted_mut = _ unquoted_mutkey mutop unquoted_mutval _
    full_quoted_mut = full_squoted_mut / full_dquoted_mut
    value_quoted_mut = value_squoted_mut / value_dquoted_mut
    full_squoted_mut = _ "'" squoted_mutkey mutop squoted_mutval "'" _
    full_dquoted_mut = _ '"' dquoted_mutkey mutop dquoted_mutval '"' _
    value_squoted_mut = _ unquoted_mutkey mutop "'" squoted_mutval "'" _
    value_dquoted_mut = _ unquoted_mutkey mutop '"' dquoted_mutval '"' _
    mutop = ":" / "==" / "="
    unquoted_mutkey = unquoted_mutkey_item+
    unquoted_mutval = unquoted_stringitem*
    unquoted_mutkey_item = unquoted_mutkey_char / escapeseq
    unquoted_mutkey_char = ~r"[^\s'\"\\=:]"
    squoted_mutkey = squoted_mutkey_item+
    squoted_mutval = squoted_stringitem*
    squoted_mutkey_item = squoted_mutkey_char / escapeseq
    squoted_mutkey_char = ~r"[^\r\n'\\=:]"
    dquoted_mutkey = dquoted_mutkey_item+
    dquoted_mutval = dquoted_stringitem*
    dquoted_mutkey_item = dquoted_mutkey_char / escapeseq
    dquoted_mutkey_char = ~r'[^\r\n"\\=:]'

    option_mut = _ optname optval_assign? _
    optname = long_optname / short_optname
    long_optname = ~r"\-\-[a-z\-]+"
    short_optname = ~r"\-[a-z]"i
    optval_assign = ~r"(\s+|=)" optval
    optval = quoted_string / unquoted_optval
    unquoted_optval = ~r"[^\-]" unquoted_stringitem*

    cd = _ "cd" _ string _
    rm = _ "rm" _ ~r"\-(h|q|b|o)" _ mutkey _
    tool = "httpie" / "curl"
    method = "get" / "post" / "put" / "delete" / "patch"
    mutkey = unquoted_mutkey / ("'" squoted_mutkey "'") /
             ('"' dquoted_mutkey '"') / optname

    string = quoted_string / unquoted_string
    quoted_string = ('"' dquoted_stringitem* '"') /
                    ("'" squoted_stringitem* "'")
    unquoted_string = unquoted_stringitem+
    dquoted_stringitem = dquoted_stringchar / escapeseq
    squoted_stringitem = squoted_stringchar / escapeseq
    unquoted_stringitem = unquoted_stringchar / escapeseq
    dquoted_stringchar = ~r'[^\r\n"\\]'
    squoted_stringchar = ~r"[^\r\n'\\]"
    unquoted_stringchar = ~r"[^\s'\"\\]"
    escapeseq = ~r"\\."
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

    def visit_cd(self, node, (_1, _2, _3, path, _4)):
        self.context_override.url = urljoin2(self.context_override.url, path)
        return node

    def visit_rm(self, node, children):
        print(children[3])
        kind = children[3].text
        name = children[5]
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

    def visit_mutkey(self, node, children):
        if len(children) == 3:
            return children[1]
        return children[0]

    def _mutate(self, node, key, op, val):
        if op == ':':
            target = self.context_override.headers
        elif op == '==':
            target = self.context_override.querystring_params
        elif op == '=':
            target = self.context_override.body_params
        target[key] = val
        return node

    def visit_unquoted_mut(self, node, (_1, key, op, val, _2)):
        return self._mutate(node, key, op, val)

    def visit_full_squoted_mut(self, node, (_1, _2, key, op, val, _3, _4)):
        return self._mutate(node, key, op, val)

    def visit_full_dquoted_mut(self, node, (_1, _2, key, op, val, _3, _4)):
        return self._mutate(node, key, op, val)

    def visit_value_squoted_mut(self, node, (_1, key, op, _2, val, _3, _4)):
        return self._mutate(node, key, op, val)

    def visit_value_dquoted_mut(self, node, (_1, key, op, _2, val, _3, _4)):
        return self._mutate(node, key, op, val)

    def visit_unquoted_mutkey(self, node, children):
        return unescape(node.text)

    def visit_squoted_mutkey(self, node, children):
        return node.text

    def visit_dquoted_mutkey(self, node, children):
        return node.text

    def visit_mutop(self, node, children):
        return node.text

    def visit_unquoted_mutval(self, node, children):
        return unescape(node.text)

    def visit_squoted_mutval(self, node, children):
        return node.text

    def visit_dquoted_mutval(self, node, children):
        return node.text

    def visit_option_mut(self, node, children):
        key = children[1]
        value = None
        # TODO: Fix the isinstance hack
        if isinstance(children[2], six.string_types):
            value = children[2]
        self.context_override.options[key] = value
        return node

    def visit_optname(self, node, children):
        return node.text

    def visit_optval_assign(self, node, (op, val)):
        return val

    def visit_optval(self, node, children):
        return node.text

    def visit_string(self, node, (val,)):
        return val

    def visit_unquoted_string(self, node, children):
        return unescape(node.text)

    def visit_quoted_string(self, node, children):
        return node.text[1:-1]

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
        if not node.expr_name and node.children:
            if len(children) == 1:
                return children[0]
            return children
        return node


def execute(command, context):
    try:
        root = grammar.parse(command)
    except ParseError:
        click.echo('Invalid command')
    else:
        visitor = ExecutionVisitor(context)
        visitor.visit(root)


def visit(command):
    root = grammar.parse(command)
    context = Context('http://httpbin.org')
    visitor = ExecutionVisitor(context)
    return visitor.visit(root)
