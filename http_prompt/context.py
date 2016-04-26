class Context(object):

    def __init__(self, url):
        self.url = url
        self.headers = {}
        self.querystring_params = {}
        self.body_params = {}
        self.options = []

    def to_args(self):
        args = [self.url] + self.options
        for k, v in self.headers.iteritems():
            args.append('%s:%s' % (k, v))
        for k, v in self.querystring_params.iteritems():
            args.append('%s==%s' % (k, v))
        for k, v in self.body_params.iteritems():
            args.append('%s=%s' % (k, v))
        return args
