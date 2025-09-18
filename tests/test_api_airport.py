import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket
from airport.serializers import (
    AirportSerializer, FlightListSerializer, TicketListSerializer
)

User = get_user_model()

AIRPORT_URL = reverse("airport:airport-list")
ROUTE_URL = reverse("airport:route-list")
AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")
ORDER_URL = reverse("airport:order-list")
TICKET_URL = reverse("airport:ticket-list")

def airport_detail_url(airport_id):
    return reverse("airport:airport-detail", args=(airport_id,))

def sample_airport(name="Test Airport", closest_big_city="CityX"):
    return Airport.objects.create(name=name, closest_big_city=closest_big_city)

def sample_user(email="user@test.com", password="pass1234"):
    return User.objects.create_user(email=email, password=password, is_active=True)

def sample_admin(email="admin@test.com", password="pass1234"):
    return User.objects.create_user(email=email, password=password, is_staff=True, is_active=True)

class UnauthenticatedAirportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class NonAdminAirportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_airport_list_forbidden(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_airport_forbidden(self):
        payload = {"name": "New Airport", "closest_big_city": "CityZ"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminAirportAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.client.force_authenticate(self.admin)

    def test_airport_list(self):
        airport1 = sample_airport()
        airport2 = sample_airport(name="Another Airport", closest_big_city="CityY")

        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airport(self):
        payload = {"name": "New Airport", "closest_big_city": "CityZ"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(airport.name, payload["name"])
        self.assertEqual(airport.closest_big_city, payload["closest_big_city"])

class AuthenticatedFlightAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

        self.source = sample_airport()
        self.dest = sample_airport(name="Dest Airport")
        self.route = Route.objects.create(source=self.source, destination=self.dest, distance=300)

        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(name="Plane1", rows=10, seats_in_row=6, airplane_type=self.airplane_type)

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2025-09-17T10:00:00Z",
            arrival_time="2025-09-17T12:00:00Z"
        )

        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(flight=self.flight, order=self.order, row=1, seat=1)

    def test_flight_list(self):
        res = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_ticket_list(self):
        res = self.client.get(TICKET_URL)
        tickets = Ticket.objects.filter(order__user=self.user)
        serializer = TicketListSerializer(tickets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_ticket_creation_row_seat_validation(self):

        payload = {"flight_id": self.flight.id, "order_id": self.order.id, "row": 20, "seat": 1}
        res = self.client.post(TICKET_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("row", res.data)

        payload = {"flight_id": self.flight.id, "order_id": self.order.id, "row": 1, "seat": 10}
        res = self.client.post(TICKET_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat", res.data)