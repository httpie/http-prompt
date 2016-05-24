import re
import six

import click

try:
    from collections import OrderedDict
except ImportError:
    from .ordereddict import OrderedDict  # For Python 2.6

from itertools import chain

from prompt_toolkit.completion import Completer, Completion

from . import options as opt


ROOT_COMMANDS = [
    ('cd', 'Change URL/path'),
    ('rm -b', 'Remove body parameter'),
    ('rm -h', 'Remove header'),
    ('rm -o', 'Remove HTTPie option'),
    ('rm -q', 'Remove querystring parameter'),
    ('curl', 'Preview curl command'),
    ('httpie', 'Preview HTTPie command'),
    ('exit', 'Exit HTTP Prompt'),
    ('help', 'List commands, option flags, and actions'),
]

ACTIONS = [
    ('delete', 'DELETE request'),
    ('get', 'GET request'),
    ('head', 'HEAD request'),
    ('patch', 'GET request'),
    ('post', 'POST request'),
    ('put', 'PUT request'),
]

# TODO: Include more header names
HEADER_NAMES = [
    ('Accept', 'Header'),
    ('Accept-Encoding', 'Header'),
    ('Authorization', 'Header'),
    ('Cache-Control', 'Header'),
    ('Cookie', 'Header'),
    ('Content-Length', 'Header'),
    ('Content-Type', 'Header'),
    ('From', 'Header'),
    ('Host', 'Header'),
    ('Origin', 'Header'),
    ('Referer', 'Header'),
    ('User-Agent', 'Header'),
]


CONTENT_TYPES = [
    'application/json',
    'application/x-www-form-urlencoded',
    'multipart/form-data',
    'text/html',
]

# TODO: Include more common header values
HEADER_VALUES = {
    'Accept': CONTENT_TYPES,
    'Content-Type': CONTENT_TYPES,
}

ROOT_COMMANDS = OrderedDict(sorted(ROOT_COMMANDS))

ACTIONS = OrderedDict(ACTIONS)

OPTION_NAMES = sorted(opt.FLAG_OPTIONS + opt.VALUE_OPTIONS)
OPTION_NAMES = OrderedDict(OPTION_NAMES)

HEADER_NAMES = OrderedDict(HEADER_NAMES)

RULES = [
    (r'((?:[^\s\'"\\=:]|(?:\\.))+):((?:[^\s\'"\\]|(?:\\.))*)$',
     'header_values'),

    (r'(get|head|post|put|patch|delete)\s+', 'concat_mutations'),
    (r'(httpie|curl)\s+', 'preview'),
    (r'rm\s+\-b\s+', 'existing_body_params'),
    (r'rm\s+\-h\s+', 'existing_header_names'),
    (r'rm\s+\-o\s+', 'existing_option_names'),
    (r'rm\s+\-q\s+', 'existing_querystring_params'),
    (r'', 'root_commands')
]


def compile_rules(rules):
    compiled_rules = []
    for pattern, meta_dict in rules:
        regex = re.compile(pattern)
        compiled_rules.append((regex, meta_dict))
    return compiled_rules

RULES = compile_rules(RULES)


def echo_help():
    """Prints a formatted list of current commands, option flags, http actions
    (and their support values)
    """
    def echo_cmds_with_explanations(summary, cmds):
        click.echo('\n{}:'.format(summary))
        for cmd, explanation in cmds:
            click.echo('\t{:<10}\t{:<20}'.format(cmd, explanation))

    click.echo('\nInteractive usage: http-prompt')
    echo_cmds_with_explanations('Commands', ROOT_COMMANDS.items())
    echo_cmds_with_explanations('Options', OPTION_NAMES.items())
    echo_cmds_with_explanations('Actions', ACTIONS.items())
    echo_cmds_with_explanations(
        'Headers',
        [
            (key, ', '.join(HEADER_VALUES[key])) if key in HEADER_VALUES else (key, '')
            for key in HEADER_NAMES.keys()
        ]
    )
    click.echo()


def fuzzyfinder(text, collection):
    """https://github.com/amjith/fuzzyfinder"""
    suggestions = []
    text = str(text) if not isinstance(text, str) else text
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        r = regex.search(item)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    return (z for _, _, z in sorted(suggestions))


def match_completions(cur_word, word_dict):
    words = word_dict.keys()
    suggestions = fuzzyfinder(cur_word, words)
    for word in suggestions:
        desc = word_dict.get(word, '')
        yield Completion(word, -len(cur_word), display_meta=desc)


class CompletionGenerator(object):

    def root_commands(self, context, match):
        return chain(
            self._generic_generate(ROOT_COMMANDS.keys(), {}, ROOT_COMMANDS),
            self.actions(context, match),
            self.concat_mutations(context, match)
        )

    def header_values(self, context, match):
        header_name = match.group(1)
        header_values = HEADER_VALUES.get(header_name)
        if header_values:
            for value in header_values:
                yield value, header_name

    def preview(self, context, match):
        return chain(
            self.actions(context, match),
            self.concat_mutations(context, match)
        )

    def actions(self, context, match):
        return self._generic_generate(ACTIONS.keys(), {}, ACTIONS)

    def concat_mutations(self, context, match):
        return chain(
            self._generic_generate(context.body_params.keys(),
                                   context.body_params, 'Body parameter'),
            self._generic_generate(context.querystring_params.keys(),
                                   context.querystring_params,
                                   'Querystring parameter'),
            self._generic_generate(HEADER_NAMES.keys(),
                                   context.headers, HEADER_NAMES),
            self._generic_generate(OPTION_NAMES.keys(),
                                   context.options, OPTION_NAMES)
        )

    def existing_body_params(self, context, match):
        return self._generic_generate(context.body_params.keys(),
                                      context.body_params, 'Body parameter')

    def existing_querystring_params(self, context, match):
        return self._generic_generate(
            context.querystring_params.keys(),
            context.querystring_params, 'Querystring parameter')

    def existing_header_names(self, context, match):
        return self._generic_generate(context.headers.keys(),
                                      context.headers, HEADER_NAMES)

    def existing_option_names(self, context, match):
        return self._generic_generate(context.headers.keys(),
                                      context.options, OPTION_NAMES)

    def _generic_generate(self, names, values, descs):
        for name in sorted(names):
            if isinstance(descs, six.string_types):
                desc = descs
            else:
                desc = descs.get(name, '')
            if name in values:
                value = values[name]
                if value is None:
                    desc += ' (on)'
                else:
                    if len(value) > 16:
                        value = value[:13] + '...'
                    desc += ' (=%s)' % value
            yield name, desc


class HttpPromptCompleter(Completer):

    def __init__(self, context):
        self.context = context
        self.comp_gen = CompletionGenerator()

    def get_completions(self, document, complete_event):
        cur_text = document.text_before_cursor
        cur_word = None
        word_dict = None

        for regex, method_name in RULES:
            match = regex.search(cur_text)
            if match:
                gen_completions = getattr(self.comp_gen, method_name)
                completions = gen_completions(self.context, match)
                word_dict = OrderedDict(completions)

                groups = match.groups()
                if len(groups) > 1:
                    cur_word = groups[-1]
                else:
                    cur_word = document.get_word_before_cursor(WORD=True)

                break

        if word_dict:
            for comp in match_completions(cur_word, word_dict):
                yield comp
