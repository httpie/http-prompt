HTTP Prompt Documentation
=========================

HTTP Prompt is an interactive command-line HTTP client featuring autocomplete
and syntax highlighting, built on HTTPie_ and prompt_toolkit_.

See it in action:

|Asciinema|


Contents
--------

.. toctree::
   :maxdepth: 3

   user-guide
   contributor-guide


Roadmap
-------

* Support for advanced HTTPie syntax, e.g, ``field:=json`` and ``field=@file.json``
* Support for cURL command and raw format preview
* Improve autocomplete
* Python syntax evaluation
* HTTP/2 support


User Support
------------

We'd love to hear more from our users! Please use the following channels for
bug reports, feature requests, and questions:

* `GitHub issues`_
* `Gitter chat room`_


Contributing
------------

Are you a developer and interested in contributing to HTTP Prompt? See
:ref:`Contributor Guide <contributor-guide>`.


Thanks
------

* HTTPie_: for designing such a user-friendly HTTP CLI
* prompt_toolkit_: for simplifying the work of building an interactive CLI
* Parsimonious_: for the PEG parser used by this project
* pgcli_: for the inspiration of this project
* Contributors_: for improving this project


.. |Asciinema| image:: https://asciinema.org/a/96613.png
    :target: https://asciinema.org/a/96613?theme=monokai&size=medium&autoplay=1&speed=1.5

.. _Contributors: https://github.com/eliangcs/http-prompt/graphs/contributors
.. _GitHub issues: https://github.com/eliangcs/http-prompt/issues
.. _Gitter chat room: https://gitter.im/eliangcs/http-prompt
.. _HTTPie: https://httpie.org
.. _Parsimonious: https://github.com/erikrose/parsimonious
.. _pgcli: http://pgcli.com
.. _prompt_toolkit: https://github.com/jonathanslenders/python-prompt-toolkit
