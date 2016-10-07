import io
import re
import sys

import click

from subprocess import CalledProcessError, Popen, PIPE

from httpie.context import Environment
from httpie.core import main as httpie_main
from parsimonious.exceptions import ParseError, VisitationError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from six.moves.urllib.parse import urljoin

from .completion import ROOT_COMMANDS, ACTIONS, OPTION_NAMES, HEADER_NAMES
from .context import Context
from .context.transform import (
    extract_args_for_httpie_main,
    format_to_curl,
    format_to_httpie,
    format_to_http_prompt)
from .output import Printer, TextWriter
from .utils import unescape, unquote


grammar = r"""
    command = mutation / immutation

    mutation = concat_mut+ / nonconcat_mut
    immutation = preview / action / env / help / exit / exec / source / _

    concat_mut = option_mut / full_quoted_mut / value_quoted_mut / unquoted_mut
    nonconcat_mut = cd / rm

    preview = _ tool _ (method _)? (urlpath _)? concat_mut* redir_out? _
    action = _ method _ (urlpath _)? concat_mut* redir_out? _
    urlpath = (~r"https?://" unquoted_string) /
              (!concat_mut !redir_out string)

    help = _ "help" _
    exit = _ "exit" _
    env  = _ "env" _ (redir_out)?
    source = _ "source" _ filepath _
    exec = _ "exec" _ filepath _

    redir_out = redir_append / redir_write / pipe
    redir_append = _ ">>" _ filepath _
    redir_write = _ ">" _ filepath _
    pipe = _ "|" _ (shell_subs / shell_code) _

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
    unquoted_mutkey_item = shell_subs / unquoted_mutkey_char / escapeseq
    unquoted_mutkey_char = ~r"[^\s'\"\\=:>]"
    squoted_mutkey = squoted_mutkey_item+
    squoted_mutval = squoted_stringitem*
    squoted_mutkey_item = shell_subs / squoted_mutkey_char / escapeseq
    squoted_mutkey_char = ~r"[^\r\n'\\=:]"
    dquoted_mutkey = dquoted_mutkey_item+
    dquoted_mutval = dquoted_stringitem*
    dquoted_mutkey_item = shell_subs / dquoted_mutkey_char / escapeseq
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
    dquoted_stringitem = shell_subs / dquoted_stringchar / escapeseq
    squoted_stringitem = shell_subs / squoted_stringchar / escapeseq
    unquoted_stringitem = shell_subs / unquoted_stringchar / escapeseq
    dquoted_stringchar = ~r'[^\r\n"\\]'
    squoted_stringchar = ~r"[^\r\n'\\]"
    unquoted_stringchar = ~r"[^\s'\"\\]"
    escapeseq = ~r"\\."
    _ = ~r"\s*"

    shell_subs = "`" shell_code "`"
    shell_code = ~r"[^`]*"
"""

if sys.platform == 'win32':
    # XXX: Windows use backslashes as separators in its filesystem path, so we
    # have to avoid using backslashes to escape chars here.
    grammar += r"""
        filepath = quoted_filepath / unquoted_filepath
        quoted_filepath = ('"' dquoted_filepath_char+ '"') /
                          ("'" squoted_filepath_char+ "'")
        dquoted_filepath_char = ~r'[^\r\n"]'
        squoted_filepath_char = ~r"[^\r\n']"
        unquoted_filepath = unquoted_filepath_char+
        unquoted_filepath_char = ~r"[^\s\"]"
    """
else:
    grammar += r"""
        filepath = string
    """

grammar = Grammar(grammar)


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


if sys.platform == 'win32':  # nocover
    def normalize_filepath(path):
        return unquote(path)
else:
    def normalize_filepath(path):
        return unescape(unquote(path))


class DummyExecutionListener(object):

    def context_changed(self, context):
        pass

    def response_returned(self, context, response):
        pass


class ExecutionVisitor(NodeVisitor):

    unwrapped_exceptions = (CalledProcessError,)

    def __init__(self, context, listener=None):
        super(ExecutionVisitor, self).__init__()
        self.context = context

        self.context_override = Context(context.url)
        self.method = None
        self.tool = None
        self._output = Printer()

        # If there's a pipe, as in "httpe post | sed s/POST/GET/", this
        # variable points to the "sed" Popen object. The variable is necessary
        # because the we need to redirect Popen.stdout to Printer, which does
        # output pagination.
        self.pipe_proc = None

        self.listener = listener or DummyExecutionListener()

        # Last response object returned by HTTPie
        self.last_response = None

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, new_output):
        if self._output:
            self._output.close()
        self._output = new_output

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
        self.output.write(generate_help_text())
        return node

    def _redirect_output(self, filepath, mode):
        filepath = normalize_filepath(filepath)
        self.output = TextWriter(open(filepath, mode))

    def visit_redir_append(self, node, children):
        self._redirect_output(children[3], 'ab')
        return node

    def visit_redir_write(self, node, children):
        self._redirect_output(children[3], 'wb')
        return node

    def visit_pipe(self, node, children):
        cmd = children[3]
        self.pipe_proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
        self.output = TextWriter(self.pipe_proc.stdin)
        return node

    def visit_exec(self, node, children):
        path = normalize_filepath(children[3])
        with io.open(path, encoding='utf-8') as f:
            # Wipe out context first
            execute('rm *', self.context, self.listener)
            for line in f:
                execute(line, self.context, self.listener)
        return node

    def visit_source(self, node, children):
        path = normalize_filepath(children[3])
        with io.open(path, encoding='utf-8') as f:
            for line in f:
                execute(line, self.context, self.listener)
        return node

    def visit_env(self, node, children):
        text = format_to_http_prompt(self.context)
        self.output.write(text)
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

    def _visit_mut_key_or_val(self, node, children):
        return unescape(''.join([c for c in children]))

    visit_unquoted_mutkey = _visit_mut_key_or_val
    visit_unquoted_mutval = _visit_mut_key_or_val
    visit_squoted_mutkey = _visit_mut_key_or_val
    visit_squoted_mutval = _visit_mut_key_or_val
    visit_dquoted_mutkey = _visit_mut_key_or_val
    visit_dquoted_mutval = _visit_mut_key_or_val

    def visit_mutop(self, node, children):
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

    def visit_filepath(self, node, children):
        return children[0]

    def visit_string(self, node, children):
        return children[0]

    def visit_quoted_filepath(self, node, children):
        return node.text[1:-1]

    def visit_unquoted_filepath(self, node, children):
        return node.text

    def visit_unquoted_string(self, node, children):
        return unescape(''.join(children))

    def visit_quoted_string(self, node, children):
        return self._visit_mut_key_or_val(node, children[0][1])

    def _visit_stringitem(self, node, children):
        child = children[0]
        if hasattr(child, 'text'):
            return child.text
        return child

    visit_unquoted_mutkey_item = _visit_stringitem
    visit_unquoted_stringitem = _visit_stringitem
    visit_squoted_mutkey_item = _visit_stringitem
    visit_squoted_stringitem = _visit_stringitem
    visit_dquoted_mutkey_item = _visit_stringitem
    visit_dquoted_stringitem = _visit_stringitem

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

    def _call_httpie_main(self):
        context = self._final_context()
        args = extract_args_for_httpie_main(context, self.method)
        env = Environment(stdout=self.output, stdin=sys.stdin,
                          is_windows=False)
        env.stdout_isatty = self.output.isatty()
        env.stdin_isatty = sys.stdin.isatty()

        # XXX: httpie_main() doesn't provide an API for us to get the
        # HTTP response object, so we use this super dirty hack -
        # sys.settrace() to intercept get_response() that is called in
        # httpie_main() internally. The HTTP response intercepted is
        # assigned to self.last_response, which self.listener may be
        # interested in.
        sys.settrace(self._trace_get_response)
        try:
            httpie_main(args, env=env)
        finally:
            sys.settrace(None)

    def visit_immutation(self, node, children):
        self.output.close()
        if self.pipe_proc:
            Printer().write(self.pipe_proc.stdout.read())
        return node

    def visit_preview(self, node, children):
        context = self._final_context()
        if self.tool == 'httpie':
            command = format_to_httpie(context, self.method)
        else:
            assert self.tool == 'curl'
            command = format_to_curl(context, self.method)
        self.output.write(command)
        return node

    def visit_action(self, node, children):
        self._call_httpie_main()
        if self.last_response:
            self.listener.response_returned(self.context, self.last_response)
        return node

    def visit_shell_subs(self, node, children):
        cmd = children[1]
        p = Popen(cmd, shell=True, stdout=PIPE)
        return p.stdout.read().decode('utf-8').rstrip()

    def _is_backticks_cmd_preceded_with_pipe_redir(self, node):
        left_hand_input = node.full_text[:node.start]
        right_hand_input = node.full_text[node.end:]
        start_backticks = re.search(r"\|.*`\s*$", left_hand_input)
        end_backticks = re.search(r"`\s*$", right_hand_input)
        if start_backticks is not None and end_backticks is not None:
            return True
        return False

    def visit_shell_code(self, node, children):
        return node.text

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
            elif issubclass(exc_class, IOError):
                msg = str(err).splitlines()[0]

                # Remove the exception class name at the beginning
                msg = msg[msg.find(':') + 2:]
                click.secho(msg, err=True, fg='red')
            else:
                # TODO: Better error message
                click.secho(str(err), err=True, fg='red')
        except CalledProcessError as err:
            click.secho(err.output + ' (exit status %d)' % err.returncode,
                        fg='red')
