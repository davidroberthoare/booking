from django.db import models
from django.contrib.auth.models import User


class Period(models.Model):
    name = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['start_time']


class Timeslot(models.Model):
    date = models.DateField()
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    limit = models.IntegerField(default=5)
    note = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.period}"

    class Meta:
        ordering = ['date', 'period']
        unique_together = (
            'date',
            'period',
        )


class Booking(models.Model):
    statuses = [
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No-Show'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    service = models.CharField(max_length=100, blank=True, null=True)
    checkin = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20,
                              blank=True,
                              null=True,
                              choices=statuses)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.timeslot}"

    class Meta:
        ordering = ['timeslot', 'user']
