from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, RedirectView

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('favicon.ico',
         RedirectView.as_view(url='/static/img/favicon/favicon.ico',
                              permanent=False),
         name='favicon'),
    path('test', views.test),
    path('home', views.home, name='home'),
    path('home/<str:date>', views.home, name='home'),
    # path('login',
    #      auth_views.LoginView.as_view(template_name='core/login.html'),
    #      name='login'),
    # path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register', views.register, name='register'),
    # path('profile', views.profile, name='profile'),
    # path('password_reset/',
    #      auth_views.PasswordChangeView.as_view(),
    #      name='password_reset'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('booking/<int:id>/add', views.add_booking.as_view()),
    path('booking/<int:id>/add/manager', views.add_booking_manager.as_view()),
    path('booking/<int:id>/cancel', views.cancel_booking),
    path('booking/<int:pk>/edit', views.edit_booking.as_view()),
    path('api/bookings/', views.api_get_bookings),
    path('timeslot/<str:date>/<int:period>/add', views.add_timeslot.as_view()),
    path('timeslot/<int:id>', views.timeslot),
    path('timeslot/<int:pk>/edit', views.edit_timeslot.as_view()),
    path('timeslot/<int:id>/delete', views.delete_timeslot),
  path('accounts/register_manager', views.register_manager, name='register_manager'),
]
