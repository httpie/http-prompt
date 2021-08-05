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
            if not self.url:
                schemes = spec.get('schemes')
                scheme = schemes[0] if schemes else 'https'
                self.url = (scheme + '://' +
                            spec.get('host', 'http://localhost:8000') +
                            spec.get('basePath', ''))

            base_path_tokens = list(filter(lambda s: s,
                                    spec.get('basePath', '').split('/')))
            paths = spec.get('paths')
            if paths:
                for path in paths:
                    path_tokens = (base_path_tokens +
                                   list(filter(lambda s: s, path.split('/'))))
                    if path == '/':  # Path is a trailing slash
                        path_tokens.insert(len(base_path_tokens), '/')
                    elif path[-1] == '/':  # Path ends with a trailing slash
                        path_tokens[-1] = path_tokens[-1] + '/'
                    self.root.add_path(*path_tokens)
                    endpoint = dict(paths[path])
                    # path parameters (apply to all paths if not overriden)
                    # exclude $ref as we have no system to handle that now
                    global_parameters = list(endpoint.pop('parameters', []))
                    # not used
                    endpoint.pop('servers', None)
                    endpoint.pop('$ref', None)
                    endpoint.pop('summary', None)
                    endpoint.pop('description', None)
                    for method, info in endpoint.items():
                        params = info.get('parameters', [])
                        params = list(global_parameters + params)
                        if params:
                            def parameter_key(i): return (
                                i.get('$ref', None),
                                i.get('name', None),
                                i.get('in', None)
                            )
                            # parameter is overriden based on $ref/in/name value
                            # last value (local definition) takes precedence
                            params_map = {parameter_key(p): p for p in params}
                            params = params_map.values()
                            for param in params:
                                if param.get('$ref'):
                                    for section in param.get('$ref').split('/'):
                                        param = param.get(
                                            section) if not section == '#' else spec

                                if param.get('in') != 'path':
                                    # Note that for completion mechanism, only
                                    # name/node_type is used
                                    # Parameters from methods/location
                                    # are merged
                                    full_path = path_tokens + [param['name']]
                                    self.root.add_path(*full_path,
                                                       node_type='file')
        elif not self.url:
            self.url = 'http://localhost:8000'

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
