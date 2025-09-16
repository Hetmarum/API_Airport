from rest_framework import serializers
from django.contrib.auth import get_user_model
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)

User = get_user_model()


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")

class AirportMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = AirportMiniSerializer(read_only=True)
    destination = AirportMiniSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="source", write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), source="destination", write_only=True
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "source_id", "destination_id")


class RouteListSerializer(serializers.ModelSerializer):
    source = AirportMiniSerializer(read_only=True)
    destination = AirportMiniSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteMiniSerializer(serializers.ModelSerializer):
    source = AirportMiniSerializer(read_only=True)
    destination = AirportMiniSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("source", "destination")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all(), source="airplane_type", write_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "airplane_type_id",
        )
        read_only_fields = ("capacity",)


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "capacity", "airplane_type")


class AirplaneMiniSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Airplane
        fields = ("name", "capacity", "airplane_type")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id",)

    def to_representation(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(), source="route", write_only=True
    )
    airplane_id = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all(), source="airplane", write_only=True
    )
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(), source="crew", many=True, write_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "route_id",
            "airplane_id",
            "crew_ids",
        )


class FlightListSerializer(FlightSerializer):
    route = RouteMiniSerializer(read_only=True)
    airplane = AirplaneMiniSerializer(read_only=True)
    crew = CrewListSerializer(many=True, read_only=True)


class FlightMiniSerializer(serializers.ModelSerializer):
    route = RouteMiniSerializer(read_only=True)
    airplane = AirplaneMiniSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = ("route", "airplane", "departure_time", "arrival_time")


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class OrderMiniSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ("created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    order = OrderSerializer(read_only=True)

    flight_id = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(), source="flight", write_only=True
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order", write_only=True
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order", "flight_id", "order_id")


class TicketListSerializer(serializers.ModelSerializer):
    flight = FlightMiniSerializer(read_only=True)
    order = OrderMiniSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
