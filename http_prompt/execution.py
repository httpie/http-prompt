import re

import click
import six

from httpie.context import Environment
from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError, VisitationError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from six import BytesIO
from six.moves.urllib.parse import urljoin

from .context import Context
from .utils import unescape


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mut+ / nonconcat_mut
    immutation = preview / action

    concat_mut = option_mut / full_quoted_mut / value_quoted_mut / unquoted_mut
    nonconcat_mut = cd / rm
    preview = _ tool _ (method _)? (urlpath _)? concat_mut*
    action = _ method _ (urlpath _)? concat_mut*
    urlpath = (~r"https?://" unquoted_string) / (!concat_mut string)

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

    option_mut = flag_option_mut / value_option_mut
    flag_option_mut = _ flag_optname _
    flag_optname = "--json" / "-j" / "--form" / "-f" / "--verbose" / "-v" /
                   "--headers" / "-h" / "--body" / "-b" / "--stream" / "-S" /
                   "--download" / "-d" / "--continue" / "-c" / "--follow" /
                   "--check-status" / "--ignore-stdin" / "--help" /
                   "--version" / "--traceback" / "--debug"
    value_option_mut = _ value_optname ~r"(\s+|=)" string _
    value_optname = "--pretty" / "--style" / "-s" / "--print" / "-p" /
                    "--output" / "-o" / "--session" / "--session-read-only" /
                    "--auth" / "-a" / "--auth-type" / "--proxy" / "--verify" /
                    "--cert" / "--cert-key" / "--timeout"

    cd = _ "cd" _ string _
    rm = _ "rm" _ ~r"\-(h|q|b|o)" _ mutkey _
    tool = "httpie" / "curl"
    method = ~r"get"i / ~r"head"i / ~r"post"i / ~r"put"i / ~r"delete"i /
             ~r"patch"i
    mutkey = unquoted_mutkey / ("'" squoted_mutkey "'") /
             ('"' dquoted_mutkey '"') / flag_optname / value_optname

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
    url = urljoin(base, path, **kwargs)
    if url.endswith('/') and not path.endswith('/'):
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

    def visit_urlpath(self, node, children):
        path = node.text
        self.context_override.url = urljoin2(self.context_override.url, path)
        return node

    def visit_cd(self, node, children):
        _, _, _, path, _ = children
        self.context_override.url = urljoin2(self.context_override.url, path)
        return node

    def visit_rm(self, node, children):
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
        if isinstance(children[0], list):
            return children[0][1]
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

    def visit_unquoted_mut(self, node, children):
        _, key, op, val, _ = children
        return self._mutate(node, key, op, val)

    def visit_full_squoted_mut(self, node, children):
        _, _, key, op, val, _, _ = children
        return self._mutate(node, key, op, val)

    def visit_full_dquoted_mut(self, node, children):
        _, _, key, op, val, _, _ = children
        return self._mutate(node, key, op, val)

    def visit_value_squoted_mut(self, node, children):
        _, key, op, _, val, _, _ = children
        return self._mutate(node, key, op, val)

    def visit_value_dquoted_mut(self, node, children):
        _, key, op, _, val, _, _ = children
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

    def visit_flag_option_mut(self, node, children):
        _, key, _ = children
        self.context_override.options[key] = None
        return node

    def visit_flag_optname(self, node, children):
        return node.text

    def visit_value_option_mut(self, node, children):
        _, key, _, val, _ = children
        self.context_override.options[key] = val
        return node

    def visit_value_optname(self, node, children):
        return node.text

    def visit_string(self, node, children):
        return children[0]

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
                command = ['http'] + context.httpie_args(self.method,
                                                         quote=True)
            else:
                assert self.tool == 'curl'
                command = ['curl'] + context.curl_args(self.method, quote=True)
            click.echo(' '.join(command))
        else:
            assert children[0].expr_name == 'action'
            output = BytesIO()
            try:
                env = Environment(stdout=output, is_windows=False)
                httpie_main(context.httpie_args(self.method), env=env)
                content = output.getvalue()
            finally:
                output.close()

            # XXX: Work around a bug of click.echo_via_pager(). When you pass
            # a bytestring to echo_via_pager(), it converts the bytestring with
            # str(b'abc'), which makes it "b'abc'".
            if six.PY2:
                content = unicode(content, 'utf-8')
            else:
                content = str(content, 'utf-8')
            click.echo_via_pager(content)

    def generic_visit(self, node, children):
        if not node.expr_name and node.children:
            if len(children) == 1:
                return children[0]
            return children
        return node


def execute(command, context):
    try:
        root = grammar.parse(command)
    except ParseError as err:
        # TODO: Better error message
        part = command[err.pos:err.pos + 10]
        click.secho('Syntax error near "%s"' % part, err=True, fg='red')
    else:
        visitor = ExecutionVisitor(context)
        try:
            visitor.visit(root)
        except VisitationError as err:
            exc_class = err.original_class
            if exc_class is KeyError:
                # XXX: Need to parse VisitationError error message to get the
                # original error message as VisitationError doesn't hold the
                # original exception object
                key = re.search(r"KeyError: '(.*)'", str(err)).group(1)
                click.secho("Key '%s' not found" % key, err=True,
                            fg='red')
            else:
                # TODO: Better error message
                click.secho(str(err), err=True, fg='red')
