
import sys
import six

from httpie.context import Environment
from httpie.core import main as httpie_main
from six import BytesIO

def request(nodeVisitor, context, method):
    output = BytesIO()
    content = None

    try:
        env = Environment(stdout=output, is_windows=False)

        # XXX: httpie_main() doesn't provide an API for us to get the
        # HTTP response object, so we use this super dirty hack -
        # sys.settrace() to intercept get_response() that is called in
        # httpie_main() internally. The HTTP response intercepted is
        # assigned to nodeVisitor.last_response, which may be useful for
        # nodeVisitor.listener.
        sys.settrace(nodeVisitor._trace_get_response)
        try:
            httpie_main(context.httpie_args(method), env=env)
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



