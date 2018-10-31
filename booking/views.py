from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.views.generic import TemplateView, ListView, CreateView, DeleteView
from django.contrib.auth.urls import views as auth_views
from django.views import View
from booking.forms import RegistrationForm, ReservationForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from .models import HotelOwner, Hotel, Reservation, ReservationDays
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy, reverse
from datetime import timedelta, date
from django import forms
from datetime import datetime
from django.shortcuts import get_object_or_404


class Home(ListView):
    template_name = 'booking/home.html'
    context_object_name = 'all_hotels'

    def get_queryset(self):
        return Hotel.objects.all()


class HotelCreate(CreateView):
    model = Hotel
    fields = ('hotel_name',
              'hotel_country',
              'hotel_city',
              'hotel_room_sgl',
              'hotel_room_dbl',
              'hotel_room_twin',
              'hotel_room_tpl',
              'hotel_room_qdbl',
              'hotel_room_family',
              'hotel_room_apartment',
              )
    success_url = reverse_lazy('booking:home')

    def form_valid(self, form):
        form.instance.hotel_owner = self.request.user
        return super(HotelCreate, self).form_valid(form)


class ReservationCreate(CreateView):
    form_class = ReservationForm
    model = Reservation

    success_url = reverse_lazy('booking:home')

    def form_valid(self, form, **kwargs):
        pknum = self.kwargs.get('hotel_id', )
        hotel = Hotel.objects.get(pk=pknum)
        form.instance.reservation_hotel = hotel
        form.instance.reservation_owner = self.request.user

        start_date = form.instance.reservation_from
        end_date = form.instance.reservation_to
        template_room_type = form.instance.reservation_room

        model_room_counter = 0

        if template_room_type == "room_sgl":
            model_room_counter = hotel.hotel_room_sgl
        elif template_room_type == "room_dbl":
            model_room_counter = hotel.hotel_room_dbl
        elif template_room_type == "room_twin":
            model_room_counter = hotel.hotel_room_twin
        elif template_room_type == "room_tpl":
            model_room_counter = hotel.hotel_room_tpl
        elif template_room_type == "room_qdbl":
            model_room_counter = hotel.hotel_room_qdbl
        elif template_room_type == "room_family":
            model_room_counter = hotel.hotel_room_family
        elif template_room_type == "room_apartment":
            model_room_counter = hotel.hotel_room_apartment

        reservation_room = form.cleaned_data.get('reservation_room')

        reservation_days = ReservationDays.objects.filter(reservation__reservation_room=reservation_room,
                                                          reservation__reservation_hotel=hotel)

        error = False
        date_error = False

        if end_date < start_date:
            date_error = True

        for single_date in daterange(start_date, end_date):
            counter = reservation_days.filter(reservation_dates=single_date).count()
            if counter == model_room_counter:
                error = True

        if error or date_error or model_room_counter == 0:
            if error:
                form.add_error('reservation_room', forms.ValidationError('These rooms reserved'))
            if date_error:
                form.add_error('reservation_from', forms.ValidationError('End date must be greater then start date'))
            return super(ReservationCreate, self).form_invalid(form)
        else:
            response = super(ReservationCreate, self).form_valid(form)
            for single_date in daterange(start_date, end_date):
                if start_date != end_date:
                    ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date, )
            thisReservationDays = ReservationDays.objects.filter(reservation=form.instance)
            print(str(thisReservationDays))
            return response


class ReservationDelete(DeleteView):
    model = Reservation
    template_name = 'booking/delete_reservation.html'

    def get_success_url(self):
        return reverse('booking:profile')


class Profile(ListView):
    template_name = 'booking/profile.html'
    context_object_name = 'my_reservations'

    def get_queryset(self):
        return Reservation.objects.filter(reservation_owner=self.request.user)


class LoginUserView(auth_views.LoginView):
    template_name = 'booking/login.html'


class LogoutUserView(auth_views.LogoutView):
    template_name = 'booking/logout.html'


class ReservationListView(ListView):
    context_object_name = 'all_reservations'

    def get_queryset(self):
        return Reservation.objects.all()


class RegisterUserView(View):

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking:login')
        else:
            return redirect('booking:register')

    def get(self, request):
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'booking/reg_form.html', args)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
    yield end_date
