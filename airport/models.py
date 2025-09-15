from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=63, unique=True)
    closest_big_city = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departures"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arrivals"
    )
    distance = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.source}-{self.destination}"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination airports must be different")


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63, unique=True)
    rows = models.PositiveIntegerField(default=1)
    seats_in_row = models.PositiveIntegerField(default=1)
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    def __str__(self):
        return f"{self.airplane_type} {self.name}"

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} {self.user}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )

    class Meta:
        ordering = ("departure_time", "arrival_time", "route", "airplane")

    def __str__(self):
        return f"Flight {self.route} {self.id}"

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time")


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        ordering = ["row", "seat", "flight", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="unique_ticket_per_seat_flight"
            )
        ]

    def __str__(self):
        return f"Ticket {self.id}: {self.flight} - (row: {self.row} seat: {self.seat})"

    @staticmethod
    def validate_seat_and_row(row: int, seat: int, airplane, error_to_raise):
        if not (1 <= row <= airplane.rows):
            raise error_to_raise(
                {"row": f"row must be in range [1, {airplane.rows}], not {row}"}
            )

        if not (1 <= seat <= airplane.seats_in_row):
            raise error_to_raise(
                {"seat": f"seat must be in range [1, {airplane.seats_in_row}], not {seat}"}
            )

    def clean(self):
        airplane = self.flight.airplane
        Ticket.validate_seat_and_row(self.row, self.seat, airplane, ValidationError)

        if Ticket.objects.filter(
                flight=self.flight, row=self.row, seat=self.seat
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                {"seat": "This seat is already taken for this flight"}
            )

        if self.flight.tickets.exclude(pk=self.pk).count() >= airplane.rows * airplane.seats_in_row:
            raise ValidationError("No seats available on this flight")

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)
