from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .admin import MemberAdmin
from .models import Member, MembershipType

User = get_user_model()


class MemberModelTests(TestCase):
    def test_str(self):
        member = Member(name="Acme Corp")
        self.assertEqual(str(member), "Acme Corp")

    def test_default_membership_type(self):
        member = Member.objects.create(name="Test Member")
        self.assertEqual(member.membership_type, MembershipType.COMMUNITY)

    def test_ordering(self):
        Member.objects.create(name="Zebra", sort_order=2)
        Member.objects.create(name="Alpha", sort_order=1)
        Member.objects.create(name="Beta", sort_order=1)
        names = list(Member.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha", "Beta", "Zebra"])

    def test_optional_fields_blank(self):
        member = Member.objects.create(name="Minimal")
        self.assertEqual(member.link, "")
        self.assertEqual(member.description, "")
        self.assertIsNone(member.logo)

    def test_membership_type_choices(self):
        self.assertEqual(
            [c[0] for c in MembershipType.choices],
            ["platinum", "gold", "silver", "bronze", "community"],
        )

    def test_sort_order_default(self):
        member = Member.objects.create(name="Default Order")
        self.assertEqual(member.sort_order, 0)


class MemberAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MemberAdmin(Member, self.site)
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username="admin", password="password", email="admin@test.com"
        )

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display, ("name", "membership_type", "sort_order")
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("membership_type",))

    def test_list_editable(self):
        self.assertEqual(self.admin.list_editable, ("sort_order",))

    def test_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("name",))

    def test_changelist_view(self):
        Member.objects.create(name="Gold Member", membership_type=MembershipType.GOLD)
        Member.objects.create(
            name="Silver Member", membership_type=MembershipType.SILVER
        )
        request = self.factory.get("/admin/members/member/")
        request.user = self.superuser
        response = self.admin.changelist_view(request)
        self.assertEqual(response.status_code, 200)

    def test_changelist_filter_by_type(self):
        Member.objects.create(name="Gold One", membership_type=MembershipType.GOLD)
        Member.objects.create(name="Silver One", membership_type=MembershipType.SILVER)
        request = self.factory.get(
            "/admin/members/member/", {"membership_type": "gold"}
        )
        request.user = self.superuser
        response = self.admin.changelist_view(request)
        self.assertEqual(response.status_code, 200)


class GetMemberQuerysetTests(TestCase):
    """Test the _get_member_queryset helper used by both plugins."""

    def setUp(self):
        from .cms_components import _get_member_queryset

        self.get_qs = _get_member_queryset
        self.gold1 = Member.objects.create(
            name="Gold Corp", membership_type=MembershipType.GOLD
        )
        self.silver1 = Member.objects.create(
            name="Silver Inc", membership_type=MembershipType.SILVER
        )
        self.community1 = Member.objects.create(
            name="Community Org", membership_type=MembershipType.COMMUNITY
        )
        self.bronze1 = Member.objects.create(
            name="Bronze Ltd", membership_type=MembershipType.BRONZE
        )

    # --- no filters ---

    def test_no_filters_returns_all(self):
        qs = self.get_qs({})
        self.assertEqual(qs.count(), 4)

    # --- membership_types filter ---

    def test_filter_single_type(self):
        qs = self.get_qs({"membership_types": ["gold"]})
        self.assertEqual(list(qs.values_list("name", flat=True)), ["Gold Corp"])

    def test_filter_multiple_types(self):
        qs = self.get_qs({"membership_types": ["gold", "silver"]})
        names = set(qs.values_list("name", flat=True))
        self.assertEqual(names, {"Gold Corp", "Silver Inc"})

    def test_filter_empty_list_returns_all(self):
        qs = self.get_qs({"membership_types": []})
        self.assertEqual(qs.count(), 4)

    # --- max_items ---

    def test_max_items_limits_results(self):
        qs = self.get_qs({"max_items": 2})
        self.assertEqual(len(qs), 2)

    def test_max_items_none_returns_all(self):
        qs = self.get_qs({"max_items": None})
        self.assertEqual(qs.count(), 4)

    def test_max_items_greater_than_total(self):
        qs = self.get_qs({"max_items": 100})
        self.assertEqual(len(qs), 4)

    def test_max_items_one(self):
        qs = self.get_qs({"max_items": 1})
        self.assertEqual(len(qs), 1)

    # --- combined filters ---

    def test_type_and_max_items(self):
        qs = self.get_qs(
            {"membership_types": ["gold", "silver", "bronze"], "max_items": 2}
        )
        self.assertEqual(len(qs), 2)
        for member in qs:
            self.assertIn(member.membership_type, ["gold", "silver", "bronze"])

    def test_type_filter_with_no_matches(self):
        qs = self.get_qs({"membership_types": ["platinum"]})
        self.assertEqual(qs.count(), 0)

    # --- require_logo ---

    def test_require_logo_excludes_without_logo(self):
        qs = self.get_qs({}, require_logo=True)
        self.assertEqual(qs.count(), 0)

    def test_require_logo_with_type_filter(self):
        qs = self.get_qs({"membership_types": ["gold"]}, require_logo=True)
        self.assertEqual(qs.count(), 0)
