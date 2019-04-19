SCIM 2.0 Filter Parser
======================

|travis| |codecov|

.. |travis| image:: https://travis-ci.com/15five/scim2-filter-parser.svg?branch=master
  :target: https://travis-ci.com/15five/scim2-filter-parser

.. |codecov| image:: https://codecov.io/gh/15five/scim2-filter-parser/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/15five/scim2-filter-parser

SCIM 2.0 defines queries that look like this::

    'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

These can be hard to work with and covert into SQL to run against a database.

That's where SCIM 2.0 Filter Parser (SFP) can help.

SFP is broken up into four modules, each handling a different part of
translating a SCIM call into a SQL query.

The first step is tokenization or lexical analysis where the filter query
is broken down into many tokens that make it up.

::

    python -m scim2_filter_parser.lexer 'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

    Token(type='ATTRNAME', value='emails', lineno=1, index=0)
    Token(type='LBRACKET', value='[', lineno=1, index=6)
    Token(type='ATTRNAME', value='type', lineno=1, index=7)
    Token(type='EQ', value='eq', lineno=1, index=12)
    Token(type='COMP_VALUE', value='work', lineno=1, index=15)
    Token(type='AND', value='and', lineno=1, index=22)
    Token(type='ATTRNAME', value='value', lineno=1, index=26)
    Token(type='CO', value='co', lineno=1, index=32)
    Token(type='COMP_VALUE', value='@example.com', lineno=1, index=35)
    Token(type='RBRACKET', value=']', lineno=1, index=49)
    Token(type='OR', value='or', lineno=1, index=51)
    Token(type='ATTRNAME', value='ims', lineno=1, index=54)
    Token(type='LBRACKET', value='[', lineno=1, index=57)
    Token(type='ATTRNAME', value='type', lineno=1, index=58)
    Token(type='EQ', value='eq', lineno=1, index=63)
    Token(type='COMP_VALUE', value='xmpp', lineno=1, index=66)
    Token(type='AND', value='and', lineno=1, index=73)
    Token(type='ATTRNAME', value='value', lineno=1, index=77)
    Token(type='CO', value='co', lineno=1, index=83)
    Token(type='COMP_VALUE', value='@foo.com', lineno=1, index=86)
    Token(type='RBRACKET', value=']', lineno=1, index=96)


The second step is to convert that series of tokens into a abstract syntax tree.

::

    python -m scim2_filter_parser.parser 'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

    Filter(expr=LogExpr, negated=False, namespace=None)
        LogExpr(op='or', expr1=Filter, expr2=Filter)
            Filter(expr=Filter, negated=False, namespace=None)
                Filter(expr=Filter, negated=False, namespace=AttrPath)
                    Filter(expr=LogExpr, negated=False, namespace=None)
                        LogExpr(op='and', expr1=Filter, expr2=Filter)
                            Filter(expr=AttrExpr, negated=False, namespace=None)
                                AttrExpr(value='eq', attr_path=AttrPath, comp_value=CompValue)
                                    AttrPath(attr_name='type', sub_attr=None, uri=None)
                                    CompValue(value='work')
                            Filter(expr=AttrExpr, negated=False, namespace=None)
                                AttrExpr(value='co', attr_path=AttrPath, comp_value=CompValue)
                                    AttrPath(attr_name='value', sub_attr=None, uri=None)
                                    CompValue(value='@example.com')
                    AttrPath(attr_name='emails', sub_attr=None, uri=None)
            Filter(expr=Filter, negated=False, namespace=None)
                Filter(expr=Filter, negated=False, namespace=AttrPath)
                    Filter(expr=LogExpr, negated=False, namespace=None)
                        LogExpr(op='and', expr1=Filter, expr2=Filter)
                            Filter(expr=AttrExpr, negated=False, namespace=None)
                                AttrExpr(value='eq', attr_path=AttrPath, comp_value=CompValue)
                                    AttrPath(attr_name='type', sub_attr=None, uri=None)
                                    CompValue(value='xmpp')
                            Filter(expr=AttrExpr, negated=False, namespace=None)
                                AttrExpr(value='co', attr_path=AttrPath, comp_value=CompValue)
                                    AttrPath(attr_name='value', sub_attr=None, uri=None)
                                    CompValue(value='@foo.com')
                    AttrPath(attr_name='ims', sub_attr=None, uri=None)

The third step is to transpile this AST into a language of our choice.
The above query is transpiled to SQL below.

::

    python -m scim2_filter_parser.transpiler 'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

    ((emails.type = {0}) AND (emails.value LIKE {1})) OR ((ims.type = {2}) AND (ims.value LIKE {3}))
    {0: 'work', 1: '%@example.com%', 2: 'xmpp', 3: '%@foo.com%'}

The fourth step is to take what is a segment of a SQL WHERE clause and complete
the rest of the SQL query.

::

    python -m scim2_filter_parser.query 'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

    >>>SELECT users.*
            FROM users
            LEFT JOIN emails ON emails.user_id = users.id
    LEFT JOIN schemas ON schemas.user_id = users.id
    WHERE ((emails.type = work) AND (emails.value LIKE %@example.com%)) OR ((ims.type = xmpp) AND (ims.value LIKE %@foo.com%));<<<

Please note that SFP does not build SQL queries with parameters pre-injected. That would create a SQL injection attack vulnerability.
Instead a `Query` object is created and can be forced to display itself as seen above by `print`ing the query object.

---

This project is still in its alpha stage of life and should be used accordingly.


