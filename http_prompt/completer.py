from __future__ import unicode_literals

from prompt_toolkit.contrib.completers import WordCompleter


class HttpPromptCompleter(WordCompleter):

    def __init__(self):
        super(HttpPromptCompleter, self).__init__(['hello', 'world'])
