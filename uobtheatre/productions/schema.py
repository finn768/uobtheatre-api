import graphene
from graphene import relay
from graphene_django import DjangoListField, DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from uobtheatre.bookings.schema import ConcessionTypeNode
from uobtheatre.productions.models import (
    CastMember,
    CrewMember,
    CrewRole,
    Performance,
    PerformanceSeatGroup,
    Production,
    ProductionTeamMember,
    Warning,
)
from uobtheatre.utils.schema import (
    GrapheneImageField,
    GrapheneImageFieldNode,
    GrapheneImageMixin,
)


class CrewRoleNode(DjangoObjectType):
    class Meta:
        model = CrewRole
        interfaces = (relay.Node,)


class CastMemberNode(GrapheneImageMixin, DjangoObjectType):
    profile_picture = GrapheneImageField(GrapheneImageFieldNode)

    class Meta:
        model = CastMember
        interfaces = (relay.Node,)


class ProductionTeamMemberNode(DjangoObjectType):
    class Meta:
        model = ProductionTeamMember
        interfaces = (relay.Node,)


class CrewMemberNode(DjangoObjectType):
    class Meta:
        model = CrewMember
        interfaces = (relay.Node,)


class WarningNode(DjangoObjectType):
    class Meta:
        model = Warning
        interfaces = (relay.Node,)


class ProductionNode(GrapheneImageMixin, DjangoObjectType):
    cover_image = GrapheneImageField(GrapheneImageFieldNode)
    featured_image = GrapheneImageField(GrapheneImageFieldNode)
    poster_image = GrapheneImageField(GrapheneImageFieldNode)

    warnings = DjangoListField(WarningNode)
    crew = DjangoListField(CrewMemberNode)
    cast = DjangoListField(CastMemberNode)
    production_team = DjangoListField(ProductionTeamMemberNode)

    start = graphene.DateTime()
    end = graphene.DateTime()

    def resolve_start(self, info):
        return self.start_date()

    def resolve_end(self, info):
        return self.end_date()

    class Meta:
        model = Production
        filter_fields = {
            "id": ("exact",),
            "slug": ("exact",),
        }
        fields = "__all__"
        interfaces = (relay.Node,)


class ConcessionTypeBookingType(graphene.ObjectType):
    concession = graphene.Field(ConcessionTypeNode)
    price = graphene.Int()
    price_pounds = graphene.String()

    def resolve_price_pounds(self, info):
        return "%.2f" % (self.price / 100)


class PerformanceSeatGroupNode(DjangoObjectType):
    capacity_remaining = graphene.Int()
    concession_types = graphene.List(ConcessionTypeBookingType)

    def resolve_concession_types(self, info):
        return [
            ConcessionTypeBookingType(
                concession=concession,
                price=self.performance.price_with_concession(concession, self.price),
            )
            for concession in self.performance.concessions()
        ]

    def resolve_capacity_remaining(self, info):
        return self.performance.capacity_remaining(self.seat_group)

    class Meta:
        model = PerformanceSeatGroup
        fields = (
            "capacity",
            "capacity_remaining",
            "concession_types",
            "seat_group",
        )
        filter_fields = {}  # type: ignore
        interfaces = (relay.Node,)


class PerformanceNode(DjangoObjectType):
    capacity_remaining = graphene.Int()
    ticket_options = graphene.List(PerformanceSeatGroupNode)
    min_seat_price = graphene.Int()

    def resolve_ticket_options(self, info, **kwargs):
        return self.performance_seat_groups.all()

    def resolve_capacity_remaining(self, info):
        return self.capacity_remaining()

    def resolve_min_seat_price(self, info):
        return self.min_seat_price()

    class Meta:
        model = Performance
        filter_fields = {
            "id": ("exact",),
            "start": ("exact", "year__gt"),
        }
        exclude = ("performance_seat_groups", "bookings")
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    productions = DjangoFilterConnectionField(ProductionNode)
    performances = DjangoFilterConnectionField(PerformanceNode)

    production = graphene.Field(ProductionNode, slug=graphene.String(required=True))

    def resolve_production(self, info, slug):
        return Production.objects.get(slug=slug)
