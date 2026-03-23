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
        Member.objects.create(name="Silver Member", membership_type=MembershipType.SILVER)
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


class MemberComponentQueryTests(TestCase):
    """Test the get_members query logic used by components."""

    def setUp(self):
        self.gold1 = Member.objects.create(
            name="Gold Corp", membership_type=MembershipType.GOLD
        )
        self.silver1 = Member.objects.create(
            name="Silver Inc", membership_type=MembershipType.SILVER
        )
        self.community1 = Member.objects.create(
            name="Community Org", membership_type=MembershipType.COMMUNITY
        )

    def test_filter_all_members(self):
        qs = Member.objects.all()
        self.assertEqual(qs.count(), 3)

    def test_filter_by_membership_type(self):
        qs = Member.objects.filter(membership_type=MembershipType.GOLD)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "Gold Corp")

    def test_filter_excludes_no_logo(self):
        qs = Member.objects.exclude(logo__isnull=True)
        self.assertEqual(qs.count(), 0)

    def test_filter_by_type_and_logo(self):
        qs = Member.objects.filter(
            membership_type=MembershipType.GOLD
        ).exclude(logo__isnull=True)
        self.assertEqual(qs.count(), 0)

    def test_all_membership_types_queryable(self):
        for mt in MembershipType:
            qs = Member.objects.filter(membership_type=mt)
            self.assertIsNotNone(qs)
