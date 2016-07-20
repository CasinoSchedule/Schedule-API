from django.db import models
import datetime
from profiles.models import ManagerProfile, EmployeeProfile


class Schedule(models.Model):
    """
    A weekly schedule. Made up of 7 days, starting from Monday.
    """
    manager = models.ForeignKey(ManagerProfile, null=True, blank=True)

    # Only active schedules are visible to employees
    active = models.BooleanField(default=False)

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
        return "schedule {}, from {} through {}".format(
            self.id,
            self.workday_set.first().day_date,
            self.workday_set.last().day_date
        )


class WorkDay(models.Model):
    """
    A single day of work. Part of a week schedule, with multiple shifts
    attached.
    """

    day_date = models.DateField(unique=True)

    # Must have schedule so they are created together.
    schedule = models.ForeignKey(Schedule)

    class Meta:
        ordering = ["day_date"]

    def __str__(self):
        return "{}".format(self.day_date)


class Shift(models.Model):
    """
    A single shift for one employee.
    """
    starting_time = models.TimeField()
    length = models.IntegerField(default=8)

    day = models.ForeignKey(WorkDay)
    employee = models.ForeignKey(EmployeeProfile)

    visible = models.BooleanField(default=False)

    # location = models.CharField(max_length=255, blank=True, null=True)
    # skills_required = models.CharField(max_length=255)
    # options_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def calendar_date(self):
        return "{}-{}-{}".format(self.day.day_date.year,
                                 self.day.day_date.month,
                                 self.day.day_date.day)

    @property
    def end_time(self):
        dt = datetime.datetime.combine(
            self.day.day_date, self.starting_time
        ) + datetime.timedelta(hours=self.length
                               )
        return dt.time()

    @property
    def called_out(self):
        # Should return [False, 'Pending', 'Approved', 'Rejected']
        callout = CallOut.objects.filter(shift=self).first()
        if callout:
            return self.callout.status.title
        else:
            return False

    def __str__(self):
        return "{}, {}, {}".format(self.id, self.employee, self.day)


class EOList(models.Model):
    day = models.ForeignKey(WorkDay)

    # Add later for day, swing, grave
    # work_period = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, {}".format(self.id, self.day.day_date)


class EOEntry(models.Model):
    """
    status can be ['submitted', 'approved', 'removed']
    """
    eo_list = models.ForeignKey(EOList)
    shift = models.ForeignKey(Shift)
    status = models.CharField(max_length=25, default="submitted")
    # position = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        default_related_name = 'eo_entries'
        unique_together = ('shift', 'eo_list')


class Status(models.Model):
    """
    Possible values: ['Pending', 'Approved', 'Rejected']
    """
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class CallOutType(models.Model):
    """
    Different types of CallOuts:
    ['unpaid', 'pto', 'FMLA']
    """
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class CallOut(models.Model):
    shift = models.OneToOneField(Shift)

    status = models.ForeignKey(Status, null=True)
    # Switch to one to one field?
    call_type = models.ForeignKey(CallOutType)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class DayOfWeek(models.Model):
    """
    The days, in order are:
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    """
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class TimeOffRequest(models.Model):
    employee = models.ForeignKey(EmployeeProfile)
    days = models.ManyToManyField(WorkDay)
    status = models.ForeignKey(Status)


class Department(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)


class Area(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    department = models.ForeignKey(Department)

# Shift has to have area
# Employee can have one department, changeable if they switch.



# class ShiftTrade(models.Model):
#     initiating_employee = models.ForeignKey(EmployeeProfile, related_name="initiator")
#     responding_employee = models.ForeignKey(EmployeeProfile, related_name="responder")
#     shift = models.ForeignKey(Shift)
#
#

