"""Functions that transform a Context object to a different representation."""

import six

from http_prompt.utils import smart_quote


def _noop(s):
    return s


def _extract_httpie_options(context, quote=False, join_key_value=False,
                            excluded_keys=None):
    if quote:
        quote_func = smart_quote
    else:
        quote_func = _noop

    if join_key_value:
        def form_new_opts(k, v): return [k + '=' + v]
    else:
        def form_new_opts(k, v): return [k, v]

    excluded_keys = excluded_keys or []

    opts = []
    for k, v in sorted(six.iteritems(context.options)):
        if k not in excluded_keys:
            if v is not None:
                v = quote_func(v)
                new_opts = form_new_opts(k, v)
            else:
                new_opts = [k]
        opts += new_opts
    return opts


def _extract_httpie_request_items(context, quote=False):
    if quote:
        quote_func = smart_quote
    else:
        quote_func = _noop

    items = []
    operators_and_items = [
        # (separator, dict_of_request_items)
        ('==', context.querystring_params),
        ('=', context.body_params),
        (':', context.headers)
    ]
    for sep, item_dict in operators_and_items:
        for k, value in sorted(six.iteritems(item_dict)):
            if isinstance(value, (list, tuple)):
                for v in value:
                    item = quote_func('%s%s%s' % (k, sep, v))
                    items.append(item)
            else:
                item = quote_func('%s%s%s' % (k, sep, value))
                items.append(item)
    return items


def extract_args_for_httpie_main(context, method=None):
    """Transform a Context object to a list of arguments that can be passed to
    HTTPie main function.
    """
    args = _extract_httpie_options(context)

    if method:
        args.append(method.upper())

    args.append(context.url)
    args += _extract_httpie_request_items(context)
    return args


def format_to_curl(context, method=None):
    """Format a Context object to a cURL command."""
    raise NotImplementedError("curl format is not supported yet")


def format_to_raw(context, method=None):
    """Format a Context object to HTTP raw text."""
    raise NotImplementedError("raw format is not supported yet")


def format_to_httpie(context, method=None):
    """Format a Context object to an HTTPie command."""
    cmd = ['http'] + _extract_httpie_options(context, quote=True,
                                             join_key_value=True)
    if method:
        cmd.append(method.upper())
    cmd.append(context.url)
    cmd += _extract_httpie_request_items(context, quote=True)
    return ' '.join(cmd) + '\n'


def format_to_http_prompt(context, excluded_options=None):
    """Format a Context object to HTTP Prompt commands."""
    cmds = _extract_httpie_options(context, quote=True, join_key_value=True,
                                   excluded_keys=excluded_options)
    cmds.append('cd ' + smart_quote(context.url))
    cmds += _extract_httpie_request_items(context, quote=True)
    return '\n'.join(cmds) + '\n'
