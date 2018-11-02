from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from datetime import datetime
import datetime
from django.forms import DateTimeInput
from django.db.models.signals import post_save
from django.dispatch import receiver


class HotelOwner(AbstractUser):
    hasHotel = models.BooleanField(default=False)

    class Meta:
        app_label = 'booking'
        permissions = ("has_hotel", "Has hotel."),


class Hotel(models.Model):
    hotel_owner = models.ForeignKey(HotelOwner, on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=120)
    hotel_country = models.CharField(max_length=50)
    hotel_city = models.CharField(max_length=100)
    hotel_room_sgl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_dbl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_twin = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_tpl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_qdbl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_family = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    hotel_room_apartment = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return self.hotel_name


class Reservation(models.Model):
    ROOM_CHOICES = (
        ('room_sgl', 'Single room'),
        ('room_dbl', 'Double room'),
        ('room_twin', 'Twin room'),
        ('room_tpl', 'Triple room'),
        ('room_qdbl', 'Quad room'),
        ('room_family', 'Family room'),
        ('room_apartment', 'Apartment'),
    )
    reservation_owner = models.ForeignKey(HotelOwner, on_delete=models.CASCADE)
    reservation_hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    reservation_from = models.DateField()
    reservation_to = models.DateField()
    reservation_room = models.CharField(max_length=20, blank=False, choices=ROOM_CHOICES)

    @property
    def is_before(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d") < self.reservation_from.strftime("%Y-%m-%d")

    @property
    def is_after(self):
        now = datetime.datetime.now()
        print("is_after: ")
        print("now: " + now.strftime("%Y-%m-%d"))
        print("res_to: " + self.reservation_to.strftime("%Y-%m-%d"))
        return now.strftime("%Y-%m-%d") > self.reservation_to.strftime("%Y-%m-%d")

    @property
    def has_opinion(self):
        opinion = Opinion.objects.filter(opinion_to=self)
        count = opinion.count()
        return count == 1


class ReservationDays(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    reservation_dates = models.DateField()

    def __str__(self):
        return str(self.reservation_dates)


class Opinion(models.Model):
    ROOM_CHOICES = (
        ('very_bad', 'Very Bad'),
        ('badly', 'Badly'),
        ('moderation', 'Moderation'),
        ('good', 'Good'),
        ('very_good', 'Very Good'),
        ('excellent', 'Excellent'),
    )
    opinion_to = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    opinion_date = models.DateField()
    opinion_content = models.TextField()
    opinion_rating = models.CharField(max_length=20, blank=False, choices=ROOM_CHOICES)
