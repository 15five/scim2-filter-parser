SCIM 2.0 Filters
================

|travis| |codecov|

.. |travis| image:: https://travis-ci.com/15five/scim2-filter-parser.svg?branch=master
  :target: https://travis-ci.com/15five/scim2-filter-parser

.. |codecov| image:: https://codecov.io/gh/15five/scim2-filter-parser/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/15five/scim2-filter-parser

SCIM 2.0 defines queries that look like this::

    'userType eq "Employee" and (emails.type eq "work")'

These can be hard to work with.

