from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Available(models.Model):
    """
    The shift periods that an employee can work.
    ['Day', 'Swing', 'Grave']
    """
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class EmployeeStatus(models.Model):
    """
    ['Full-time', 'On-call', or 'Extra Board']
    """
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class ManagerProfile(models.Model):

    user = models.OneToOneField(User, null=True)

    position_title = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey('schedules.Department', null=True, blank=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # mi = models.CharField(max_length=1, null=True, blank=True)
    # cloudinary_image

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def user_name(self):
        if hasattr(self, 'user'):
            return self.user.username
        else:
            return False


class EmployeeProfile(models.Model):

    user = models.OneToOneField(User, null=True, blank=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    photo_url = models.URLField(blank=True, null=True)
    # mi = models.CharField(max_length=1, null=True, blank=True)
    # cloudinary_image

    employee_id = models.CharField(max_length=255, null=True, blank=True)
    position_title = models.CharField(max_length=255, null=True, blank=True)

    # Full-time, On-call, or Extra Board
    employment_status = models.ForeignKey(EmployeeStatus, null=True, blank=True)

    department = models.ForeignKey('schedules.Department', null=True, blank=True)

    phone_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    phone_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)

    regular_days_off = models.ManyToManyField('schedules.DayOfWeek',
                                              blank=True)
    availability = models.ManyToManyField(Available, blank=True)

    was_invited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def days_off(self):
        return self.regular_days_off.values_list('title', flat=True)

    @property
    def shift_title(self):
        return self.availability.values_list('title', flat=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
