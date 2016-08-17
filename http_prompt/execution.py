import re
import sys

import click
import six

from httpie.context import Environment
from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError, VisitationError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from six import BytesIO
from six.moves.urllib.parse import urljoin
# from pprint import pprint
# import inspect

from .outputmethod import OutputMethod
from .commandio import put as command_ouput
from .completion import ROOT_COMMANDS, ACTIONS, OPTION_NAMES, HEADER_NAMES
from .context import Context
from .utils import unescape, unquote


grammar = Grammar(r"""
    command = mutation / immutation

    mutation = concat_mut+ / nonconcat_mut
    immutation = preview / action / help / exit / env / _

    concat_mut = option_mut / full_quoted_mut / value_quoted_mut / unquoted_mut
    nonconcat_mut = cd / rm
    preview = _ tool _ (method _)? (urlpath _)? concat_mut* redir_out? _
    action = _ method _ (urlpath _)? concat_mut* redir_out? _
    urlpath = (~r"https?://" unquoted_string) / (!concat_mut !redir_out string)
    help = _ "help" _
    exit = _ "exit" _
    env  = _ "env" _ (redir_out)?

    redir_out = _ (redir_append_file / redir_file) _ string _
    redir_file = _ ">" _
    redir_append_file = _ ">>" _
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
                    "--output" / "-o" / "--session-read-only" / "--session" /
                    "--auth-type" / "--auth" / "-a" / "--proxy" / "--verify" /
                    "--cert" / "--cert-key" / "--timeout"

    cd = _ "cd" _ string _
    rm = (_ "rm" _ "*" _) / (_ "rm" _ ~r"\-(h|q|b|o)" _ mutkey _)
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


def generate_help_text():
    """Return a formatted string listing commands, HTTPie options, and HTTP
    actions.
    """
    def generate_cmds_with_explanations(summary, cmds):
        text = '{0}:\n'.format(summary)
        for cmd, explanation in cmds:
            text += '\t{0:<10}\t{1:<20}\n'.format(cmd, explanation)
        return text + '\n'

    text = generate_cmds_with_explanations('Commands', ROOT_COMMANDS.items())
    text += generate_cmds_with_explanations('Options', OPTION_NAMES.items())
    text += generate_cmds_with_explanations('Actions', ACTIONS.items())
    text += generate_cmds_with_explanations('Headers', HEADER_NAMES.items())
    return text


class DummyExecutionListener(object):

    def url_changed(self, old_url, context):
        pass

    def context_changed(self, context):
        pass

    def response_returned(self, context, response):
        pass


class ExecutionVisitor(NodeVisitor):

    def __init__(self, context, listener=None):
        super(ExecutionVisitor, self).__init__()
        self.context = context

        self.context_override = Context(context.url)
        self.method = None
        self.tool = None
        self.output_methods = [OutputMethod.echo]
        self.output_file_path = None

        self.listener = listener if listener else DummyExecutionListener()
        self.last_response = None

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

        if self.context_override.url != self.context.url:
            self.listener.url_changed(self.context.url, self.context_override)

        return node

    def visit_rm(self, node, children):
        children = children[0]
        kind = children[3].text

        if kind == '*':
            # Clear context
            for target in [self.context.headers,
                           self.context.querystring_params,
                           self.context.body_params,
                           self.context.options]:
                target.clear()
            return node

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

    def visit_help(self, node, children):
        click.echo_via_pager(generate_help_text())
        return node

    def visit_redir_file(self, node, children):
        self.output_methods = [OutputMethod.write_file]
        return node

    def visit_redir_append_file(self, node, children):
        self.output_methods = [OutputMethod.append_file]
        return node

    def visit_redir_out(self, node, children):
        path = node.text.strip()
        self.output_file_path = unquote(path[2:])

        return node

    def visit_env(self, node, children):
        self.context = self._final_context()
        context = self._final_context()

        args = context.httpie_data_args(quote=True)
        command_ouput('\n'.join(args), self.output_methods, self.output_file_path)
        return node

    def visit_exit(self, node, children):
        self.context.should_exit = True
        return node

    def visit_mutkey(self, node, children):
        if isinstance(children[0], list):
            return children[0][1]
        return children[0]

    def _mutate(self, node, key, op, val):
        if op == ':':
            self.context_override.headers[key] = val
        elif op == '=':
            self.context_override.body_params[key] = val
        elif op == '==':
            # You can have multiple querystring params with the same name,
            # so we use a list to store multiple values (#20)
            params = self.context_override.querystring_params
            if key not in params:
                params[key] = [val]
            else:
                params[key].append(val)
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
        return unescape(node.text)

    def visit_dquoted_mutkey(self, node, children):
        return unescape(node.text)

    def visit_mutop(self, node, children):
        return node.text

    def visit_unquoted_mutval(self, node, children):
        return unescape(node.text)

    def visit_squoted_mutval(self, node, children):
        return unescape(node.text)

    def visit_dquoted_mutval(self, node, children):
        return unescape(node.text)

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
        self.listener.context_changed(self.context)
        return node

    def _final_context(self):
        context = self.context.copy()
        context.update(self.context_override)
        return context

    def _trace_get_response(self, frame, event, arg):
        func_name = frame.f_code.co_name
        if func_name == 'get_response':
            if event == 'call':
                return self._trace_get_response
            elif event == 'return':
                self.last_response = arg

    def visit_immutation(self, node, children):
        context = self._final_context()
        child_type = children[0].expr_name

        if child_type == 'preview':
            if self.tool == 'httpie':
                command = ['http'] + context.httpie_args(self.method,
                                                         quote=True)
            else:
                assert self.tool == 'curl'
                command = ['curl'] + context.curl_args(self.method, quote=True)
            command_ouput(' '.join(command), self.output_methods, self.output_file_path)
        elif child_type == 'action':
            output = BytesIO()
            try:
                env = Environment(stdout=output, is_windows=False)

                # XXX: httpie_main() doesn't provide an API for us to get the
                # HTTP response object, so we use this super dirty hack -
                # sys.settrace() to intercept get_response() that is called in
                # httpie_main() internally. The HTTP response intercepted is
                # assigned to self.last_response, which may be useful for
                # self.listener.
                sys.settrace(self._trace_get_response)
                try:
                    httpie_main(context.httpie_args(self.method), env=env)
                finally:
                    sys.settrace(None)

                content = output.getvalue()
            finally:
                output.close()

            # XXX: Work around a bug of click.echo_via_pager(). When you pass
            # a bytestring to echo_via_pager(), it converts the bytestring with
            # str(b'abc'), which makes it "b'abc'".
            if six.PY2:
                content = unicode(content, 'utf-8')  # noqa
            else:
                content = str(content, 'utf-8')
            command_ouput(content, self.output_methods, self.output_file_path)
            # click.echo_via_pager(content)

            if self.last_response:
                self.listener.response_returned(self.context,
                                                self.last_response)

        return node

    def generic_visit(self, node, children):
        if not node.expr_name and node.children:
            if len(children) == 1:
                return children[0]
            return children
        return node


def execute(command, context, listener=None):
    try:
        root = grammar.parse(command)
    except ParseError as err:
        # TODO: Better error message
        part = command[err.pos:err.pos + 10]
        click.secho('Syntax error near "%s"' % part, err=True, fg='red')
    else:
        visitor = ExecutionVisitor(context, listener=listener)
        try:
            # print('PARSEDDD')
            # pprint (visitor.__dict__)
            # pprint(inspect.getsourcelines(visitor.visit));
            visitor.visit(root)
        except VisitationError as err:
            exc_class = err.original_class
            if exc_class is KeyError:
                # XXX: Need to parse VisitationError error message to get the
                # original error message as VisitationError doesn't hold the
                # original exception object
                key = re.search(r"KeyError: u?'(.*)'", str(err)).group(1)
                click.secho("Key '%s' not found" % key, err=True,
                            fg='red')
            else:
                # TODO: Better error message
                click.secho(str(err), err=True, fg='red')
