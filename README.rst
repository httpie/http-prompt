HTTP Prompt (A WORK IN PROGRESS)
==============================

|Build Status| |Coverage|

An interactive command-line HTTP client featuring auto-completion and syntax
highlighting.

Use case::

    $ http-prompt http://httpbin.org
    Welcome to HTTP Prompt!
    http://httpbin.org> cd post
    http://httpbin.org/post> name=bob email=bob@example.com
    http://httpbin.org/post> sex==M --form
    http://httpbin.org/post> post
    HTTP/1.1 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Origin: *
    Connection: keep-alive
    Content-Length: 473
    Content-Type: application/json
    Date: Wed, 27 Apr 2016 09:04:29 GMT
    Server: nginx

    {
        "args": {
            "sex": "M"
        },
        "data": "",
        "files": {},
        "form": {
            "email": "bob@example.com",
            "name": "bob"
        },
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Content-Length": "32",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Host": "httpbin.org",
            "User-Agent": "HTTPie/0.9.3"
        },
        "json": null,
        "origin": "x.x.x.x",
        "url": "http://httpbin.org/post?sex=M"
    }


.. |Build Status| image:: https://api.travis-ci.org/eliangcs/http-prompt.svg?branch=master
    :target: https://travis-ci.org/eliangcs/http-prompt

.. |Coverage| image:: https://coveralls.io/repos/github/eliangcs/http-prompt/badge.svg?branch=master
    :target: https://coveralls.io/github/eliangcs/http-prompt?branch=master
