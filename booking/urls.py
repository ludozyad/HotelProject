from django.urls import path
from . import views
app_name = 'booking'
urlpatterns = [
    path('home/', views.Home.as_view(), name='home'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('add/', views.HotelCreate.as_view(), name='hotel_add'),
    path('reservation/list/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservation/<int:hotel_id>/', views.ReservationCreate.as_view(), name='reservation_add'),
    path('profile/delete/<int:pk>/', views.ReservationDelete.as_view(), name='reservation_delete'),
]
