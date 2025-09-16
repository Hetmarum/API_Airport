from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from airport.permissions import IsOwner
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
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    OrderSerializer,
    TicketSerializer,
    TicketListSerializer,
)

User = get_user_model()


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminUser]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        return (
            Route.objects
            .select_related("source", "destination")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminUser]


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        return (
            Flight.objects
            .select_related(
                "route",
                "route__source",
                "route__destination",
                "airplane",
                "airplane__airplane_type",
            )
            .prefetch_related("crew")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(
                "tickets__flight__route__source",
                "tickets__flight__route__destination",
                "tickets__flight__airplane__airplane_type",
                "tickets__flight__crew",
            )
        )


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsOwner]


    def get_queryset(self):
        user = self.request.user
        return (
            Ticket.objects
            .filter(order__user=user)
            .select_related(
                "flight",
                "flight__route",
                "flight__route__source",
                "flight__route__destination",
                "flight__airplane",
                "flight__airplane__airplane_type",
                "order",
                "order__user",
            )
            .prefetch_related("flight__crew")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        return TicketSerializer
