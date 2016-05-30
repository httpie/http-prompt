import six

from .utils import smart_quote


class Context(object):

    def __init__(self, url=None):
        self.url = url
        self.headers = {}
        self.querystring_params = {}
        self.body_params = {}
        self.options = {}

        # Indicate if main program should be terminated
        self.should_exit = False

    def __eq__(self, other):
        return (self.url == other.url and
                self.headers == other.headers and
                self.options == other.options and
                self.querystring_params == other.querystring_params and
                self.body_params == other.body_params and
                self.should_exit == other.should_exit)

    def copy(self):
        context = Context(self.url)
        context.headers = self.headers.copy()
        context.querystring_params = self.querystring_params.copy()
        context.body_params = self.body_params.copy()
        context.options = self.options.copy()
        context.should_exit = self.should_exit
        return context

    def update(self, context):
        if context.url:
            self.url = context.url

        self.headers.update(context.headers)
        self.querystring_params.update(context.querystring_params)
        self.body_params.update(context.body_params)
        self.options.update(context.options)
        self.should_exit = self.should_exit

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
