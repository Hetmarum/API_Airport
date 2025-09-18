from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from airport.permissions import IsOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

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
    """
    CRUD for airports.
    """

    queryset = Airport.objects.all().order_by("id")
    serializer_class = AirportSerializer
    permission_classes = [IsAdminUser]


class RouteViewSet(viewsets.ModelViewSet):
    """
    CRUD for routes.
    """

    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        return Route.objects.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD for airplane types.
    """

    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    CRUD for airplanes.
    """

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
    """
    CRUD for crew members.
    """

    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminUser]


class TicketsFlightsPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    """
    CRUD for flights with route, airplane, crew info, and city in list view.
    """

    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = TicketsFlightsPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = {
        "departure_time": ["gte", "lte"],
        "arrival_time": ["gte", "lte"],
        "route__source": ["exact"],
        "route__destination": ["exact"],
        "airplane__airplane_type": ["exact"],
    }
    ordering_fields = ["departure_time", "arrival_time"]
    search_fields = [
        "route__source__name",
        "route__destination__name",
        "airplane__name",
        "route__destination__closest_big_city",
    ]

    def get_queryset(self):
        queryset = Flight.objects.all()

        queryset = queryset.select_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type",
        )

        if self.action != "list":
            queryset = queryset.prefetch_related("crew")

        return queryset.order_by("departure_time", "arrival_time")

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD for orders, only accessible by owner or admin.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Order.objects.all()
            if user.is_staff or user.is_superuser
            else Order.objects.filter(user=user)
        )

        return queryset.select_related("user").prefetch_related(
            Prefetch(
                "tickets__flight__route",
                queryset=Route.objects.select_related("source", "destination"),
            ),
            "tickets__flight__airplane__airplane_type",
            "tickets__flight__crew",
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    """
    CRUD for tickets, only accessible by owner or admin.
    """

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsOwner]
    pagination_class = TicketsFlightsPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = {
        "flight__departure_time": ["gte", "lte"],
        "flight__arrival_time": ["gte", "lte"],
        "flight__route__source": ["exact"],
        "flight__route__destination": ["exact"],
        "flight__airplane__airplane_type": ["exact"],
        "order__user": ["exact"],
    }
    ordering_fields = ["flight__departure_time", "flight__arrival_time"]
    search_fields = [
        "flight__route__source__name",
        "flight__route__destination__name",
        "flight__airplane__name",
        "flight__route__destination__closest_big_city",
        "order__user__email",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Ticket.objects.all()
            if user.is_staff or user.is_superuser
            else Ticket.objects.filter(order__user=user)
        )

        return queryset.prefetch_related(
            Prefetch(
                "flight__route",
                queryset=Route.objects.select_related("source", "destination"),
            ),
            "flight__airplane__airplane_type",
            "flight__crew",
            Prefetch("order", queryset=Order.objects.select_related("user")),
        )

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save()
