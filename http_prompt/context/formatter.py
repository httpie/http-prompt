import six

from http_prompt.utils import smart_quote


def _format_in_curl(context):
    raise NotImplementedError("curl format is not supported yet")


def _format_in_raw(context):
    raise NotImplementedError("raw format is not supported yet")


def _extract_httpie_options(context):
    opts = []
    for k, v in sorted(six.iteritems(context.options)):
        opt = k
        if v is not None:
            opt += ' ' + smart_quote(v)
        opts.append(opt)
    return opts


def _extract_httpie_request_items(context):
    items = []
    operators_and_items = [
        # (operator, dict_of_request_items)
        ('==', context.querystring_params),
        ('=', context.body_params),
        (':', context.headers)
    ]
    for op, item_dict in operators_and_items:
        for k, value in sorted(six.iteritems(item_dict)):
            if isinstance(value, (list, tuple)):
                for v in value:
                    item = smart_quote('%s%s%s' % (k, op, v))
                    items.append(item)
            else:
                item = smart_quote('%s%s%s' % (k, op, value))
                items.append(item)
    return items


def _format_in_httpie(context, method=None):
    cmd = ['http'] + _extract_httpie_options(context)
    if method:
        cmd.append(method.upper())
    cmd.append(context.url)
    cmd += _extract_httpie_request_items(context)
    return ' '.join(cmd)


def _format_in_http_prompt(context):
    cmds = _extract_httpie_options(context)
    cmds.append('cd ' + smart_quote(context.url))
    cmds += _extract_httpie_request_items(context)
    return '\n'.join(cmds) + '\n'


_FORMATTERS = {
    'curl': _format_in_curl,
    'raw': _format_in_raw,
    'httpie': _format_in_httpie,
    'http-prompt': _format_in_http_prompt
}


def format_context(context, fmt, **kwargs):
    """Format a Context object to a string."""
    format_func = _FORMATTERS[fmt]
    return format_func(context, **kwargs)
