import re
import six

from collections import OrderedDict
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
]

ACTIONS = [
    ('delete', 'DELETE request'),
    ('get', 'GET request'),
    ('patch', 'GET request'),
    ('post', 'POST request'),
    ('put', 'PUT request'),
]

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

HEADER_VALUES = {
    'Content-Type': OrderedDict([
        ('applicaiton/json', 'Content-Type'),
        ('text/html', 'Content-Type'),
    ]),
    'User-Agent': OrderedDict([
        ('Chrome', 'User-Agent'),
        ('Firefox', 'User-Agent'),
    ]),
}

ROOT_COMMANDS = OrderedDict(sorted(ROOT_COMMANDS))

ACTIONS = OrderedDict(ACTIONS)

OPTION_NAMES = sorted(opt.FLAG_OPTIONS + opt.VALUE_OPTIONS)
OPTION_NAMES = OrderedDict(OPTION_NAMES)

HEADER_NAMES = OrderedDict(HEADER_NAMES)

RULES = [
    (r'(httpie|curl)\s+\w+\s+', 'concat_mutations'),
    (r'(httpie|curl)\s+', 'actions'),
    (r'(get|post|put|patch|delete)\s+', 'concat_mutations'),
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

    def root_commands(self, document, context):
        return chain(
            self._generic_generate(ROOT_COMMANDS.keys(), {}, ROOT_COMMANDS),
            self.actions(document, context),
            self.concat_mutations(document, context)
        )

    def actions(self, document, context):
        return self._generic_generate(ACTIONS.keys(), {}, ACTIONS)

    def concat_mutations(self, document, context):
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

    def existing_body_params(self, document, context):
        return self._generic_generate(context.body_params.keys(),
                                      context.body_params, 'Body parameter')

    def existing_querystring_params(self, document, context):
        return self._generic_generate(
            context.querystring_params.keys(),
            context.querystring_params, 'Querystring parameter')

    def existing_header_names(self, document, context):
        return self._generic_generate(context.headers.keys(),
                                      context.headers, HEADER_NAMES)

    def existing_option_names(self, document, context):
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
        cur_word = document.get_word_before_cursor(WORD=True)
        cur_text = document.text_before_cursor
        word_dict = None

        for regex, method_name in RULES:
            if regex.search(cur_text):
                gen_completions = getattr(self.comp_gen, method_name)
                completions = gen_completions(document, self.context)
                word_dict = OrderedDict(completions)
                break

        if completions:
            for comp in match_completions(cur_word, word_dict):
                yield comp
