from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
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
    queryset = Airport.objects.all().order_by("id")
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

class TicketsFlightsPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = TicketsFlightsPagination

    def get_queryset(self):
        queryset = Flight.objects.all()

        if self.action == "list":
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type"
            )
        else:
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type"
            ).prefetch_related("crew")

        return queryset.order_by("departure_time", "arrival_time")

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
    pagination_class = TicketsFlightsPagination

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Ticket.objects.all()
            if user.is_staff or user.is_superuser
            else Ticket.objects.filter(order__user=user)
        )

        return (
            queryset
            .select_related(
                "order__user",
                "flight__airplane",
                "flight__airplane__airplane_type",
                "flight__route__source",
                "flight__route__destination",
            )
            .only(
                "id", "row", "seat",
                "flight__id", "flight__departure_time", "flight__arrival_time",
                "flight__airplane__name",
                "flight__airplane__airplane_type__name",
                "flight__route__id",
                "flight__route__source__id", "flight__route__source__closest_big_city",
                "flight__route__destination__id", "flight__route__destination__closest_big_city",
                "order__id", "order__created_at",
                "order__user__id", "order__user__email"
            )
            .prefetch_related("flight__crew")
            .order_by(
                "row",
                "seat",
                "flight__departure_time",
                "flight__arrival_time",
                "flight__route_id",
                "flight__airplane_id",
                "order__created_at"
            )
        )
    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save()
