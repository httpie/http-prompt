from http_prompt.tree import Node


class Context(object):

    def __init__(self, url=None, spec=None):
        self.url = url
        self.headers = {}
        self.querystring_params = {}
        self.body_params = {}
        self.body_json_params = {}
        self.options = {}
        self.should_exit = False

        # Create a tree for supporting API spec and ls command
        self.root = Node('root')
        if spec:
            paths = spec.get('paths')
            if paths:
                for path in paths:
                    path_tokens = list(filter(lambda s: s, path.split('/')))
                    self.root.add_path(*path_tokens)
                    endpoint = paths[path]
                    for method, info in endpoint.items():
                        params = info.get('parameters')
                        if params:
                            for param in params:
                                full_path = path_tokens + [param['name']]
                                self.root.add_path(*full_path,
                                                   node_type='file')

    def __eq__(self, other):
        return (self.url == other.url and
                self.headers == other.headers and
                self.options == other.options and
                self.querystring_params == other.querystring_params and
                self.body_params == other.body_params and
                self.body_json_params == other.body_json_params and
                self.should_exit == other.should_exit)

    def copy(self):
        context = Context(self.url)
        context.headers = self.headers.copy()
        context.querystring_params = self.querystring_params.copy()
        context.body_params = self.body_params.copy()
        context.body_json_params = self.body_json_params.copy()
        context.options = self.options.copy()
        context.should_exit = self.should_exit
        return context

    def update(self, context):
        if context.url:
            self.url = context.url

        self.headers.update(context.headers)
        self.querystring_params.update(context.querystring_params)
        self.body_params.update(context.body_params)
        self.body_json_params.update(context.body_json_params)
        self.options.update(context.options)
        self.should_exit = self.should_exit
