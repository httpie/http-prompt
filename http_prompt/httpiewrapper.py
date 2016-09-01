
import sys
import six

from httpie.context import Environment
from httpie.core import main as httpie_main
from six import BytesIO


def _httpie_args_from_context(context, method=None):
    # TODO: The code here is kind of duplicate with
    # http_prompt.context.formatter
    args = []

    for k, v in sorted(six.iteritems(context.options)):
        args.append(k)
        if v is not None:
            args.append(v)

    if method:
        args.append(method.upper())

    args.append(context.url)

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
                    arg = '%s%s%s' % (k, op, v)
                    args.append(arg)
            else:
                arg = '%s%s%s' % (k, op, value)
                args.append(arg)

    return args


def request(node_visitor, context, method):
    content = None
    args = _httpie_args_from_context(context, method)
    output = BytesIO()
    try:
        env = Environment(stdout=output, is_windows=False)

        # XXX: httpie_main() doesn't provide an API for us to get the
        # HTTP response object, so we use this super dirty hack -
        # sys.settrace() to intercept get_response() that is called in
        # httpie_main() internally. The HTTP response intercepted is
        # assigned to nodeVisitor.last_response, which may be useful for
        # nodeVisitor.listener.
        sys.settrace(node_visitor._trace_get_response)
        try:
            httpie_main(args, env=env)
        finally:
            sys.settrace(None)

        content = output.getvalue()
    finally:
        output.close()

        # XXX: Work around a bug of click.echo_via_pager(). When you pass
        # a bytestring to echo_via_pager(), it converts the bytestring with
        # str(b'abc'), which makes it "b'abc'".
        if six.PY2:
            content = unicode(content, 'utf-8')  # noqa
        else:
            content = str(content, 'utf-8')

    return content
