from scim2_filter_parser.query import SQLiteQuery


def short():
    filter = 'userName eq "test"'

    attr_map = {
        ('name', 'familyname', None): 'name.familyname',
        ('emails', None, None): 'emails',
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('username', None, None): 'username',
        ('title', None, None): 'title',
        ('usertype', None, None): 'usertype',
        ('schemas', None, None): 'schemas',
        ('username', None, 'urn:ietf:params:scim:schemas:core:2.0:user'): 'username',
        ('meta', 'lastmodified', None): 'meta.lastmodified',
        ('ims', 'type', None): 'ims.type',
        ('ims', 'value', None): 'ims.value',
    }

    joins = (
        'LEFT JOIN emails ON emails.user_id = users.id',
        'LEFT JOIN schemas ON schemas.user_id = users.id',
    )

    q = SQLiteQuery(filter, 'users', attr_map, joins)

    q.sql


def long():
    filter = 'emails[type eq "work" and value co "@example.com"] or ims[type eq "xmpp" and value co "@foo.com"]'

    attr_map = {
        ('name', 'familyname', None): 'name.familyname',
        ('emails', None, None): 'emails',
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('username', None, None): 'username',
        ('title', None, None): 'title',
        ('usertype', None, None): 'usertype',
        ('schemas', None, None): 'schemas',
        ('username', None, 'urn:ietf:params:scim:schemas:core:2.0:user'): 'username',
        ('meta', 'lastmodified', None): 'meta.lastmodified',
        ('ims', 'type', None): 'ims.type',
        ('ims', 'value', None): 'ims.value',
    }

    joins = (
        'LEFT JOIN emails ON emails.user_id = users.id',
        'LEFT JOIN schemas ON schemas.user_id = users.id',
    )

    q = SQLiteQuery(filter, 'users', attr_map, joins)

    q.sql

