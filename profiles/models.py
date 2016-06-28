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


class EmployeeStatus(models.Model):
    title = models.CharField(max_length=30)

class ManagerProfile(models.Model):

    user = models.OneToOneField(User, null=True)

    position_title = models.CharField(max_length=255)
    #department

    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    # mi = models.CharField(max_length=1, null=True, blank=True)
    # cloudinary_image

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class EmployeeProfile(models.Model):

    user = models.OneToOneField(User, null=True)

    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    # mi = models.CharField(max_length=1, null=True, blank=True)
    # cloudinary_image

    employee_id = models.CharField(max_length=255)
    position_title = models.CharField(max_length=255, null=True, blank=True)

    days_off = models.ManyToManyField("schedules.DayOfWeek")

    employment_status = models.ForeignKey(EmployeeStatus, null=True, blank=True)

    # availability
    # usual_shift: grave, swing, day

    # Validate these in form
    phone_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    phone_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)

    # skills

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def test(self):
        return 1

    def __str__(self):
        return self.user.username




