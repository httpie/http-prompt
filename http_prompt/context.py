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

    def httpie_args(self, method=None, quote=False):
        args = []

        for k, v in sorted(six.iteritems(self.options)):
            args.append(k)
            if v is not None:
                args.append(smart_quote(v))

        if method:
            args.append(method.upper())

        args.append(self.url)

        if quote:
            quote_arg = smart_quote
        else:
            def no_op(s): return s
            quote_arg = no_op

        operators_and_items = [
            # (operator, dict_of_request_items)
            ('==', self.querystring_params),
            ('=', self.body_params),
            (':', self.headers)
        ]

        for op, item_dict in operators_and_items:
            for k, v in sorted(six.iteritems(item_dict)):
                arg = quote_arg('%s%s%s' % (k, op, v))
                args.append(arg)

        return args

    def curl_args(self, quote=False):
        raise NotImplementedError('curl is not supported yet')
