from http_prompt.context import Context
from http_prompt.context.formatter import format_context


def test_httpie_get():
    c = Context('http://localhost/things')
    c.headers.update({
        'Authorization': 'ApiKey 1234',
        'Accept': 'text/html'
    })
    c.querystring_params.update({
        'page': '2',
        'limit': '10'
    })

    output = format_context(c, 'httpie', method='get')
    assert output == ("http GET http://localhost/things "
                      "limit==10 page==2 "
                      "Accept:text/html 'Authorization:ApiKey 1234'")


def test_httpie_post():
    c = Context('http://localhost/things')
    c.headers.update({
        'Authorization': 'ApiKey 1234',
        'Accept': 'text/html'
    })
    c.options['--form'] = None
    c.body_params.update({
        'name': 'Jane Doe',
        'email': 'jane@example.com'
    })

    output = format_context(c, 'httpie', method='post')
    assert output == ("http --form POST http://localhost/things "
                      "email=jane@example.com 'name=Jane Doe' "
                      "Accept:text/html 'Authorization:ApiKey 1234'")
