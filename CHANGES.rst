CHANGE LOG
==========

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

