from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import F, Count
from django.forms.models import model_to_dict
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.exceptions import ValidationError, PermissionDenied
from core.forms import *
from .models import *
from datetime import datetime, timedelta
from pytz import timezone

# Set timezone
tz = timezone("US/Eastern")

# Date with timezone
# date = datetime.now(tz)


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    else:
        return render(request, 'core/index.html', {})


def test(request):
    return "test"


def register(request):
    print("HELLO!")
    # return render(request, 'main/register.html', {'title' : 'Resgister'})
    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('core:home')
    else:
        form = UserForm()
        print("FORM:")
        print(form)

    return render(request, 'registration/register.html', {
        'title': 'Register',
        'form': form
    })


def password(request):
    return "password"


# utility function for user memberships
def is_member(user, groupname):
    return user.groups.filter(name=groupname).exists()


@login_required
def home(request, date=None):
    # based on the type of user, rendere different templates

    # MANAGER
    if (request.user.groups.filter(name='manager').exists()):
        today = datetime.now(tz)
        if date:
            date = datetime.strptime(date, "%d-%m-%y")
        else:
            date = today  #if we're not browsing other dates, then use today

        start = date - timedelta(days=date.weekday())  #monday
        start = start.replace(hour=0, minute=00)

        end = start + timedelta(days=5)  #friday
        end = end.replace(hour=23, minute=59)

        timeslots = Timeslot.objects.filter(
            date__week=start.isocalendar()[1]).annotate(
                available=F('limit') - Count('booking'),
                num_booked=Count('booking'))

        next_date = date + timedelta(weeks=1)
        prev_date = date - timedelta(weeks=1)

        periods = Period.objects.all()

        return render(
            request, 'core/home_manager.html', {
                'role':
                'Manager',
                'title':
                'Manager Home',
                'timeslots':
                timeslots,
                'days': [
                    start + timedelta(days=x)
                    for x in range(0, (end - start).days)
                ],
                'start':
                start,
                'next_date':
                next_date.strftime("%d-%m-%y"),
                'prev_date':
                prev_date.strftime("%d-%m-%y"),
                'periods':
                periods
            })

    # OPERATOR
    elif (request.user.groups.filter(name='operator').exists()):
        today = datetime.now(tz)
        if date:
            date = datetime.strptime(date, "%d-%m-%y")
        else:
            date = today  #if we're not browsing other dates, then use today

        bookings = Booking.objects.filter(timeslot__date__year=date.year,
                                          timeslot__date__month=date.month,
                                          timeslot__date__day=date.day)

        # print(bookings)
        next_date = date + timedelta(days=1)
        prev_date = date - timedelta(days=1)
        return render(
            request,
            'core/home_operator.html',
            {
                'today': today,
                'date': date.strftime("%A, %B %-d, %Y"),
                'next_date': next_date.strftime("%d-%m-%y"),
                'prev_date': prev_date.strftime("%d-%m-%y"),
                'role': 'Operator',
                'bookings': bookings,
                # 'timeslots': timeslots
            })
        return render(request, 'core/home_operator.html', {'role': 'Operator'})

    # USER
    else:
        today = datetime.now(tz)
        bookings = Booking.objects.filter(user=request.user,
                                          timeslot__date__gte=today)
        timeslots = Timeslot.objects.filter(date__gte=today).annotate(
            available=F('limit') - Count('booking'))

        return render(
            request, 'core/home.html', {
                'role': 'Customer',
                'title': 'Customer Home',
                'bookings': bookings,
                'timeslots': timeslots
            })


@login_required
def api_get_bookings(request):
    response = {"message": "success"}
    bookings = Booking.objects.all().values(
        'id',
        'service',
        'checkin',
        'completed',
        'status',
        'comment',
        'user__id',
        'user__first_name',
        'user__last_name',
        'timeslot__date',
        'timeslot__limit',
        'timeslot__note',
        'timeslot__period__name',
        'timeslot__period__start_time',
        'timeslot__period__end_time',
    )
    response['data'] = list(bookings)

    return JsonResponse(status=200, data=response)


class add_booking(CreateView):
    model = Booking
    fields = ['service']
    title = "Reserve this Timeslot:"  #default
    timeslot = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'Operator'
        id = self.kwargs.get('id', None)
        print("get_context_data", id)
        self.timeslot = Timeslot.objects.get(pk=id)

        # raise PermissionDenied
        #
        return context

    def form_valid(self, form):
        id = self.kwargs.get('id', None)
        print("form_valid", id)
        timeslot = Timeslot.objects.get(pk=id)
        if (timeslot):
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.timeslot = timeslot
            self.object.save()

        return redirect('core:home')


@login_required
def cancel_booking(request, id):
    booking = Booking.objects.get(pk=id, user=request.user)
    if (booking):
        booking.delete()
        return JsonResponse(status=200, data={"message": "success"})
    else:
        return JsonResponse(status=500, data={"message": "An error occurred"})


class edit_booking(UpdateView):
    model = Booking
    # fields = ['service', 'checkin', 'completed', 'status', 'comment']
    title = "Update Booking"  #default
    form_class = BookingUpdateForm

    template_name_suffix = '_update_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'Operator'
        return context

    def form_valid(self, form):
        id = self.kwargs.get('id', None)
        print("form_valid", id)

        self.object = form.save(commit=False)
        self.object.save()

        # return redirect(f"/booking/{self.object.id}/edit")
        return redirect("core:home")


class add_timeslot(CreateView):
    model = Timeslot
    title = "Create a new Timeslot:"  #default
    form_class = TimeslotForm
    date = None
    period = None

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['role'] = 'Manager'

    #     # print("get_context_data", id)
    #     return context

    def get_initial(self):
        date_str = self.kwargs.get('date', None)
        self.date = datetime.strptime(date_str, "%d-%m-%y")

        period_id = self.kwargs.get('period', None)
        self.period = Period.objects.get(pk=period_id)
        return {
            'date': self.date,
            'period': self.period,
        }

    def form_valid(self, form):
        date_str = self.kwargs.get('date', None)
        date = datetime.strptime(date_str, "%d-%m-%y")

        period_id = self.kwargs.get('period', None)
        period = Period.objects.get(pk=period_id)

        self.object = form.save(commit=False)
        self.object.date = date
        self.object.period = period
        self.object.save()

        return redirect('core:home')


@login_required
def timeslot(request, id):
    timeslot = Timeslot.objects.get(pk=id)
    bookings = Booking.objects.filter(timeslot=timeslot)

    return render(request, 'core/timeslot.html', {
        'role': 'Manager',
        'timeslot': timeslot,
        'bookings': bookings,
    })


class add_booking_manager(CreateView):
    model = Booking
    fields = ['user', 'service']
    title = "Add a reservation:"  #default
    template_name_suffix = '_manager_form'
    timeslot = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'Manager'
        id = self.kwargs.get('id', None)
        print("get_context_data", id)
        self.timeslot = Timeslot.objects.get(pk=id)

        # raise PermissionDenied
        #
        return context

    def form_valid(self, form):
        id = self.kwargs.get('id', None)
        print("form_valid", id)
        timeslot = Timeslot.objects.get(pk=id)

        # user = User.objects.create_user(username='john',
        #                          email='jlennon@beatles.com',
        #                          password='glass onion')

        if (timeslot):
            self.object = form.save(commit=False)
            # self.object.user = user
            self.object.timeslot = timeslot
            self.object.save()

        return redirect('core:home')


class edit_timeslot(UpdateView):
    model = Timeslot
    title = "Update Timeslot"  #default
    form_class = TimeslotUpdateForm
    template_name_suffix = '_update_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'Operator'
        return context

    def form_valid(self, form):
        id = self.kwargs.get('id', None)
        print("form_valid", id)

        self.object = form.save(commit=False)
        self.object.save()

        # return redirect(f"/booking/{self.object.id}/edit")
        return redirect(f"/timeslot/{self.object.id}")


@login_required
def delete_timeslot(request, id):
    if request.user.groups.filter(name='manager').exists():
        timeslot = Timeslot.objects.get(pk=id)
        if (timeslot):
            timeslot.delete()

    return redirect("core:home")


def register_manager(request):
    # return render(request, 'main/register.html', {'title' : 'Resgister'})
    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('core:home')
    else:
        form = UserForm()
        # print("FORM:")
        # print(form)

    return render(request, 'registration/register.html', {
        'title': 'Create User',
        'form': form
    })
