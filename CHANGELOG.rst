CHANGE LOG
==========

0.4.2
-----
- Drop support for Python 3.7.
- Add support for Python 3.11.

0.4.1
-----
- Migrate library to Poetry for development.  #32
- Drop support for Python 3.6.

0.4.0
-----
- Update userName to be case insensitive.  #31

BREAKING CHANGE: This allows queries that did not match rows before to
match rows now!


0.3.9
-----
- Allow the use of "$" in attribute names.  #25

0.3.8
-----
- Add development speed notice
- Fix Logical Expression precedence issue #17

0.3.7
-----
- Improve README
- Bump to latest version of Sly (0.4)
- Allow import of SQLQuery from queries package

0.3.6
-----
- Move Django to install as an extra rather than by default

0.3.5
-----
- Update the sql.Transpiler to collect namedtuples rather than tuples for attr paths

0.3.4
-----
- Update tox.ini and clean up linting errors

0.3.3
-----
- Change params on AttrPath into property

0.3.2
-----
- Add first_path method on AttrPath object

0.3.1
-----
- Change name of AttrPaths -> AttrPath and add logic to check for complexity

0.3.0
-----
- Add COMP_VALUEs to AttrPath objects

0.2.4
-----
- Add rST docs to project

0.2.3
-----
- Fix lexer error where op codes are mistaken for attrnames

0.2.2
-----
- Allow value_path to be an attr_path.

  This change is not in spec but allows us to handle things
  like 'members[value eq "6784"] eq ""' which are helpful for
  AttrPath parsing for PATCH calls.

0.2.1
-----
- Fix long staging tokening error

0.2.0
-----
- Add logic for AttrPath extractions

0.1.1
-----
- Retain capitalization in queries

0.1.0
-----

- attr_map keys now control which SQL expressions are present in output of transpiler

