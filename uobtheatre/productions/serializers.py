from rest_framework import serializers

from uobtheatre.productions.models import (
    CastMember,
    CrewMember,
    Performance,
    Production,
    Venue,
    Warning,
)
from uobtheatre.societies.serializers import SocietySerializer
from uobtheatre.utils.serializers import AppendIdSerializerMixin
from uobtheatre.venues.serializers import VenueSerializer


class CrewMemberSerialzier(serializers.ModelSerializer):
    role = serializers.StringRelatedField()

    class Meta:
        model = CrewMember
        fields = ("name", "role")


class CastMemberSerialzier(serializers.ModelSerializer):
    class Meta:
        model = CastMember
        fields = ("name", "role", "profile_picture")


class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = "__all__"


class PerformanceSerializer(AppendIdSerializerMixin, serializers.ModelSerializer):
    venue = VenueSerializer()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    class Meta:
        model = Performance
        fields = ("id", "production", "venue", "start", "end", "extra_information")


class ProductionSerializer(AppendIdSerializerMixin, serializers.ModelSerializer):
    society = SocietySerializer()
    performances = PerformanceSerializer(many=True)
    warnings = serializers.StringRelatedField(many=True)
    crew = CrewMemberSerialzier(many=True)
    cast = CastMemberSerialzier(many=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    class Meta:
        model = Production
        fields = "__all__"
        lookup_field = "email"


class PerformanceTicketTypesSerializer(serializers.ModelSerializer):
    def to_representation(self, performance):
        return {
            "capacity_remaining": performance.capacity_remaining(),
            "ticket_types": [
                {
                    "seat_group": {
                        "id": performance_seat_group.seat_group.id,
                        "name": performance_seat_group.seat_group.name,
                        "description": performance_seat_group.seat_group.description,
                        "capacity_remaining": performance.capacity_remaining(
                            performance_seat_group.seat_group
                        ),
                    },
                    "concession_types": [
                        {
                            "concession": {
                                "name": concession.name,
                                "id": concession.id,
                            },
                            "price": performance.price_with_concession(
                                concession, performance_seat_group.price
                            ),
                            "price_pounds": "%.2f"
                            % (
                                performance.price_with_concession(
                                    concession, performance_seat_group.price
                                )
                                / 100
                            ),
                        }
                        for concession in performance.concessions()
                    ],
                }
                for performance_seat_group in performance.performance_seat_groups.order_by(
                    "id"
                )
            ],
        }
