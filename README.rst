=======
zoslogs
=======


.. image:: https://img.shields.io/pypi/v/zoslogs.svg
        :target: https://pypi.python.org/pypi/zoslogs
        :alt:  Pypi

.. image:: https://github.com/Tam-Lin/zoslogs/actions/workflows/build.yml/badge.svg
        :target: https://github.com/Tam-Lin/zoslogs/actions/workflows/build.yml
        :alt: Build Status

.. image:: https://readthedocs.org/projects/zoslogs/badge/?version=latest
        :target: https://zoslogs.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


Library for parsing z/OS log files (syslog, operlog) up into individual messages.  Because logs can be messy, and
authorized programs can write whatever they want to the log, by default it will discard anything that doesn't match
what a log entry should look like, and return whatever it can make sense of.

Please note that this was written to solve a problem I was having; it's by no means perfect, but it may solve a problem
you have, too, and I do plan on continuing to improve it as I have time.  Pull requests and bug reports will certainly
be appreciated.


* Free software: Apache Software License 2.0
* Documentation: https://zoslogs.readthedocs.io.


Features
--------

* Handle compressed files
* Filtering messages



Credits
-------

Created by Kevin McKenzie
kmckenzi@us.ibm.com

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
