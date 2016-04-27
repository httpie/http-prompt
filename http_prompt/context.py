class Context(object):

    def __init__(self, url=None):
        self.url = url
        self.headers = {}
        self.querystring_params = {}
        self.body_params = {}
        self.options = []

    def copy(self):
        context = Context(self.url)
        context.headers = self.headers.copy()
        context.querystring_params = self.querystring_params.copy()
        context.body_params = self.body_params.copy()
        context.options = list(self.options)
        return context

    def update(self, context):
        if context.url:
            self.url = context.url

        self.headers.update(context.headers)
        self.querystring_params.update(context.querystring_params)
        self.body_params.update(context.body_params)

        for opt in context.options:
            if opt not in self.options:
                self.options.append(opt)

    def httpie_args(self, method=None):
        args = list(self.options)
        if method:
            args.append(method.upper())
        args.append(self.url)
        for k, v in self.headers.iteritems():
            args.append('%s:%s' % (k, v))
        for k, v in self.querystring_params.iteritems():
            args.append('%s==%s' % (k, v))
        for k, v in self.body_params.iteritems():
            args.append('%s=%s' % (k, v))
        return args

    def curl_args(self):
        raise NotImplementedError('curl is not supported yet')
