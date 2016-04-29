import six

from .utils import smart_quote


class Context(object):

    def __init__(self, url=None):
        if url.endswith('/'):
            url = url[:-1]
        self.url = url
        self.headers = {}
        self.querystring_params = {}
        self.body_params = {}
        self.options = {}

    def copy(self):
        context = Context(self.url)
        context.headers = self.headers.copy()
        context.querystring_params = self.querystring_params.copy()
        context.body_params = self.body_params.copy()
        context.options = self.options.copy()
        return context

    def update(self, context):
        if context.url:
            self.url = context.url

        self.headers.update(context.headers)
        self.querystring_params.update(context.querystring_params)
        self.body_params.update(context.body_params)
        self.options.update(context.options)

    def httpie_args(self, method=None):
        args = []

        for k, v in sorted(six.iteritems(self.options)):
            args.append(k)
            if v is not None:
                args.append(smart_quote(v))

        if method:
            args.append(method.upper())

        args.append(self.url)

        for k, v in sorted(six.iteritems(self.querystring_params)):
            args.append('%s==%s' % (k, smart_quote(v)))
        for k, v in sorted(six.iteritems(self.body_params)):
            args.append('%s=%s' % (k, smart_quote(v)))
        for k, v in sorted(six.iteritems(self.headers)):
            args.append('%s:%s' % (k, smart_quote(v)))
        return args

    def curl_args(self):
        raise NotImplementedError('curl is not supported yet')
