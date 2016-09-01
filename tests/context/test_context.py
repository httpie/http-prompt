from http_prompt.context import Context


def test_creation():
    context = Context('http://example.com')
    assert context.url == 'http://example.com'
    assert context.options == {}
    assert context.headers == {}
    assert context.querystring_params == {}
    assert context.body_params == {}
    assert not context.should_exit


def test_creation_with_longer_url():
    context = Context('http://example.com/a/b/c/index.html')
    assert context.url == 'http://example.com/a/b/c/index.html'
    assert context.options == {}
    assert context.headers == {}
    assert context.querystring_params == {}
    assert context.body_params == {}
    assert not context.should_exit


def test_eq():
    c1 = Context('http://localhost')
    c2 = Context('http://localhost')
    assert c1 == c2

    c1.options['--verify'] = 'no'
    assert c1 != c2


def test_copy():
    c1 = Context('http://localhost')
    c2 = c1.copy()
    assert c1 == c2
    assert c1 is not c2


def test_update():
    c1 = Context('http://localhost')
    c1.headers['Accept'] = 'application/json'
    c1.querystring_params['flag'] = '1'
    c1.body_params.update({
        'name': 'John Doe',
        'email': 'john@example.com'
    })

    c2 = Context('http://example.com')
    c2.headers['Content-Type'] = 'text/html'
    c2.body_params['name'] = 'John Smith'

    c1.update(c2)

    assert c1.url == 'http://example.com'
    assert c1.headers == {
        'Accept': 'application/json',
        'Content-Type': 'text/html'
    }
    assert c1.querystring_params == {'flag': '1'}
    assert c1.body_params == {
        'name': 'John Smith',
        'email': 'john@example.com'
    }
