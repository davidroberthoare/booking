from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


class UserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('service', 'checkin', 'completed', 'status', 'comment')
        widgets = {
            'checkin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'completed': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ('limit', 'note')
        # input_formats = ['%d/%m/%Y']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TimeslotUpdateForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ('limit', 'note')
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'date'}),
        }