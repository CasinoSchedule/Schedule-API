from django.db import models
import datetime
from profiles.models import ManagerProfile, EmployeeProfile


class DayOfWeek(models.Model):
    """
    One for each day of the week.
    """
    day = models.CharField(max_length=10, unique=True)
    is_weekend = models.BooleanField()
    python_int = models.IntegerField()

    def __str__(self):
        return self.day


# NOTE: I am not sure yet if schedules will be unique for each period, or will
# add another identifier so that there can be multiple schedules for each day.
# For now I will make the slightly sketchy assumption that they are unique.

class Schedule(models.Model):
    """
    A weekly schedule. Made up of 7 days, starting from Monday.
    """
    manager = models.ForeignKey(ManagerProfile, null=True, blank=True)

    # current, on_deck, expired, upcoming
    status = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def starting(self):
        start_day = self.workday_set.order_by("day_date").first()
        if start_day:
            return start_day.day_date
        else:
            return None

    def __str__(self):
        return "schedule {}. Starting {}".format(
            self.id, self.workday_set.all()[0].day_date
        )


class WorkDay(models.Model):
    """
    A single day of work. Part of a week schedule, with multiple shifts
    attached.
    """

    day_date = models.DateField(unique=True)

    day_of_the_week = models.ForeignKey(DayOfWeek)

    # Must have schedule so they are created together.
    schedule = models.ForeignKey(Schedule)

    def __str__(self):
        return "{}, {}".format(self.day_date, self.day_of_the_week)


class Shift(models.Model):
    """
    A single shift for one employee.
    """
    starting_time = models.TimeField()
    length = models.IntegerField(default=8)

    day = models.ForeignKey(WorkDay)
    employee = models.ForeignKey(EmployeeProfile)

    # location = models.CharField(max_length=255, blank=True, null=True)
    # skills_required = models.CharField(max_length=255)
    # options_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def calendar_date(self):
        return self.day.day_date

    @property
    def end_time(self):
        dt = datetime.datetime.combine(
            self.day.day_date, self.starting_time
        ) + datetime.timedelta(hours=self.length
                               )
        return dt.time()


# class EOList(models.Model):
#     position = models.CharField(max_length=50, null=True, blank=True)
#
#     # Not sure about start time. Might want to go by day instead.
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#
#
# class EOEntry(models.Model):
#     eo_list = models.ForeignKey(EOList)
#     employee = models.ForeignKey(EmployeeProfile)
#     status = models.CharField(max_length=25, default="submitted")
#     # position = models.IntegerField(null=True, blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#
#
# class CallOut(models.Model):
#     employee = models.ForeignKey(EmployeeProfile)
#     shift = models.ForeignKey(Shift)
#
#
# class Area(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#
#
# class ShiftTrade(models.Model):
#     initiating_employee = models.ForeignKey(EmployeeProfile, related_name="initiator")
#     responding_employee = models.ForeignKey(EmployeeProfile, related_name="responder")
#     shift = models.ForeignKey(Shift)
#
#
# class ShiftTime(models.Model):
#     """
#     grave, swing, day.
#     Has time periods for each and an endpoint to change them.
#     """
#     pass
