from unittest import TestCase

from django.db.models import Q
from scim2_filter_parser.transpilers.django_q_object import get_query


class TestRFCExamples(TestCase):
    attr_map = {
        ("name", "familyName", None): "name.familyname",
        ("emails", None, None): "emails",
        ("emails", "type", None): "emails.type",
        ("emails", "value", None): "emails.value",
        ("userName", None, None): "username",
        ("title", None, None): "title",
        ("userType", None, None): "usertype",
        ("schemas", None, None): "schemas",
        ("userName", None, "urn:ietf:params:scim:schemas:core:2.0:User"): "username",
        ("meta", "lastModified", None): "meta.lastmodified",
        ("ims", "type", None): "ims.type",
        ("ims", "value", None): "ims.value",
    }

    def assert_q(self, input, expected):
        self.assertEqual(expected, get_query(input, self.attr_map))

    def test_username_eq(self):
        scim = 'userName eq "bjensen"'
        django = Q(username__iexact="bjensen")
        self.assert_q(scim, django)

    def test_family_name_contains(self):
        scim = '''name.familyName co "O'Malley"'''
        django = Q(name__familyname__icontains="O'Malley")
        self.assert_q(scim, django)

    def test_family_name_contains_case_insensitive(self):
        scim = '''Name.FamilyName Co "O'Malley"'''
        django = Q(name__familyname__icontains="O'Malley")
        self.assert_q(scim, django)

    def test_username_startswith(self):
        scim = 'userName sw "J"'
        django = Q(username__istartswith="J")
        self.assert_q(scim, django)

    def test_username_endswith(self):
        scim = 'userName ew "J"'
        django = Q(username__iendswith="J")
        self.assert_q(scim, django)

    def test_username_eq_none(self):
        scim = 'userName eq "null"'
        django = Q(username__iexact=None)
        self.assert_q(scim, django)

    def test_username_eq_true(self):
        scim = 'userName eq "true"'
        django = Q(username__iexact=True)
        self.assert_q(scim, django)

    def test_username_eq_false(self):
        scim = 'userName eq "false"'
        django = Q(username__iexact=False)
        self.assert_q(scim, django)

    def test_schema_username_startswith(self):
        scim = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        django = Q(username__istartswith="J")
        self.assert_q(scim, django)

    def test_title_has_value(self):
        scim = "title pr"
        django = Q(title__isnull=False)
        self.assert_q(scim, django)

    def test_meta_last_modified_gt(self):
        scim = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        django = Q(meta__lastmodified__gt="2011-05-13T04:42:34Z")
        self.assert_q(scim, django)

    def test_meta_last_modified_ge(self):
        scim = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        django = Q(meta__lastmodified__gte="2011-05-13T04:42:34Z")
        self.assert_q(scim, django)

    def test_meta_last_modified_lt(self):
        scim = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        django = Q(meta__lastmodified__lt="2011-05-13T04:42:34Z")
        self.assert_q(scim, django)

    def test_meta_last_modified_le(self):
        scim = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        django = Q(meta__lastmodified__lte="2011-05-13T04:42:34Z")
        self.assert_q(scim, django)

    def test_title_has_value_and_user_type_eq(self):
        scim = 'title pr and userType eq "Employee"'
        django = Q(title__isnull=False) & Q(usertype__iexact="Employee")
        self.assert_q(scim, django)

    def test_title_has_value_or_user_type_eq(self):
        scim = 'title pr or userType eq "Intern"'
        django = Q(title__isnull=False) | Q(usertype__iexact="Intern")
        self.assert_q(scim, django)

    def test_schemas_eq(self):
        scim = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        django = Q(
            schemas__iexact="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
        )
        self.assert_q(scim, django)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        scim = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        django = Q(usertype__iexact="Employee") & (
            Q(emails__icontains="example.com")
            | Q(emails__value__icontains="example.org")
        )
        self.assert_q(scim, django)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        scim = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        django = ~Q(usertype__iexact="Employee") & ~(
            Q(emails__icontains="example.com")
            | Q(emails__value__icontains="example.org")
        )
        self.assert_q(scim, django)

    def test_user_type_eq_and_not_email_type_eq(self):
        scim = 'userType eq "Employee" and (emails.type eq "work")'
        django = Q(usertype__iexact="Employee") & Q(emails__type__iexact="work")
        self.assert_q(scim, django)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        scim = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = Q(usertype__iexact="Employee") & (
            Q(emails__type__iexact="work") & Q(emails__value__icontains="@example.com")
        )
        self.assert_q(scim, django)

    def test_emails_type_eq_and_value_contains_or_ims_type_eq_and_value_contains(self):
        scim = (
            'emails[type eq "work" and value co "@example.com"] or '
            'ims[type eq "xmpp" and value co "@foo.com"]'
        )
        django = (
            Q(emails__type__iexact="work") & Q(emails__value__icontains="@example.com")
        ) | (Q(ims__type__iexact="xmpp") & Q(ims__value__icontains="@foo.com"))

        self.assert_q(scim, django)


class TestUndefinedAttributes(TestCase):
    def assert_q(self, scim, attr_map, expected):
        self.assertEqual(expected, get_query(scim, attr_map))

    def test_username_eq(self):
        scim = 'userName eq "bjensen"'
        django = None
        attr_map = {}
        self.assert_q(scim, attr_map, django)

    def test_title_has_value_and_user_type_eq_1(self):
        scim = 'title pr and userType eq "Employee"'
        django = Q(title__isnull=False)
        attr_map = {("title", None, None): "title"}
        self.assert_q(scim, attr_map, django)

    def test_title_has_value_and_user_type_eq_2(self):
        scim = 'title pr and userType eq "Employee"'
        django = Q(usertype__iexact="Employee")
        attr_map = {("userType", None, None): "usertype"}
        self.assert_q(scim, attr_map, django)

    def test_schemas_eq(self):
        scim = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        django = None
        attr_map = {}
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        scim = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        django = Q(usertype__iexact="Employee") & (
            Q(emails__icontains="example.com")
            | Q(emails__value__icontains="example.org")
        )
        attr_map = {
            ("userType", None, None): "usertype",
            ("emails", None, None): "emails",
            ("emails", "value", None): "emails.value",
        }
        self.assert_q(scim, attr_map, django)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        scim = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        django = ~Q(usertype__iexact="Employee") & ~(
            Q(emails__icontains="example.com")
            | Q(emails__value__icontains="example.org")
        )
        attr_map = {
            ("userType", None, None): "usertype",
            ("emails", None, None): "emails",
            ("emails", "value", None): "emails.value",
        }
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_not_email_type_eq_1(self):
        scim = 'userType eq "Employee" and (emails.type eq "work")'
        django = Q(usertype__iexact="Employee")
        attr_map = {("userType", None, None): "usertype"}
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_not_email_type_eq_2(self):
        scim = 'userType eq "Employee" and (emails.type eq "work")'
        django = Q(emails__type__iexact="work")
        attr_map = {("emails", "type", None): "emails.type"}
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_1(self):
        scim = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = Q(usertype__iexact="Employee")
        attr_map = {("userType", None, None): "usertype"}
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_2(self):
        scim = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = Q(emails__type__iexact="work")
        attr_map = {("emails", "type", None): "emails.type"}
        self.assert_q(scim, attr_map, django)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_3(self):
        scim = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = Q(emails__type__iexact="work") & Q(
            emails__value__icontains="@example.com"
        )
        attr_map = {
            ("emails", "type", None): "emails.type",
            ("emails", "value", None): "emails.value",
        }
        self.assert_q(scim, attr_map, django)

    def test_emails_type_eq_work_value_contains_or_ims_type_eq_and_value_contains_1(
        self,
    ):
        scim = (
            'emails[type eq "work" and value co "@example.com"] or '
            'ims[type eq "xmpp" and value co "@foo.com"]'
        )
        django = Q(emails__value__icontains="@example.com") | Q(
            ims__type__iexact="xmpp"
        )
        attr_map = {
            ("emails", "value", None): "emails.value",
            ("ims", "type", None): "ims.type",
        }
        self.assert_q(scim, attr_map, django)

    def test_emails_type_eq_work_value_contains_or_ims_type_eq_and_value_contains_2(
        self,
    ):
        scim = (
            'emails[type eq "work" and value co "@example.com"] or '
            'ims[type eq "xmpp" and value co "@foo.com"]'
        )
        django = Q(emails__value__icontains="@example.com") | (
            Q(ims__type__iexact="xmpp") & Q(ims__value__icontains="@foo.com")
        )
        attr_map = {
            ("emails", "value", None): "emails.value",
            ("ims", "type", None): "ims.type",
            ("ims", "value", None): "ims.value",
        }
        self.assert_q(scim, attr_map, django)

    def test_emails_type_eq_work_value_contains_or_ims_type_eq_and_value_contains_3(
        self,
    ):
        scim = (
            'emails[type eq "work" and value co "@example.com"] or '
            'ims[type eq "xmpp" and value co "@foo.com"]'
        )
        django = (
            Q(emails__type__iexact="work") & Q(emails__value__icontains="@example.com")
        ) | Q(ims__type__iexact="xmpp")
        attr_map = {
            ("emails", "value", None): "emails.value",
            ("emails", "type", None): "emails.type",
            ("ims", "type", None): "ims.type",
        }
        self.assert_q(scim, attr_map, django)

    def test_emails_type_eq_work_value_contains_or_ims_type_eq_and_value_contains_4(
        self,
    ):
        scim = (
            'emails[type eq "work" and value co "@example.com"] or '
            'ims[type eq "xmpp" and value co "@foo.com"]'
        )
        django = Q(emails__type__iexact="work") | Q(ims__value__icontains="@foo.com")
        attr_map = {
            ("emails", "type", None): "emails.type",
            ("ims", "value", None): "ims.value",
        }
        self.assert_q(scim, attr_map, django)

    def test_email_type_eq_primary_value_eq_uuid_1(self):
        scim = (
            'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        )
        django = Q(emails__value__iexact="001750ca-8202-47cd-b553-c63f4f245940")
        attr_map = {("emails", "value", None): "emails.value"}
        self.assert_q(scim, attr_map, django)

    def test_email_type_eq_primary_value_eq_uuid_2(self):
        scim = (
            'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        )
        django = Q(emails__type__iexact="Primary")
        attr_map = {("emails", "type", None): "emails.type"}
        self.assert_q(scim, attr_map, django)


class TestAzureQueries(TestCase):
    attr_map = {
        ("emails", "type", None): "emails.type",
        ("emails", "value", None): "emails.value",
        ("externalId", None, None): "externalid",
    }

    def assert_q(self, input, expected):
        self.assertEqual(expected, get_query(input, self.attr_map))

    def test_email_type_eq_primary_value_eq_uuid(self):
        scim = (
            'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        )
        django = Q(emails__type__iexact="Primary") & Q(
            emails__value__iexact="001750ca-8202-47cd-b553-c63f4f245940"
        )
        self.assert_q(scim, django)

    def test_external_id_from_azure(self):
        scim = 'externalId eq "4d32ab19-ae09-4236-82fa-15768bc48a08"'
        django = Q(externalid__iexact="4d32ab19-ae09-4236-82fa-15768bc48a08")
        self.assert_q(scim, django)

    def test_parse_simple_email_filter_with_uuid(self):
        scim = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        django = Q(emails__value__iexact="001750ca-8202-47cd-b553-c63f4f245940")
        self.assert_q(scim, django)
