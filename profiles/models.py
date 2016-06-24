from django.db import models


class ManagerProfile(models.Model):
    name = models.CharField(max_length=255)
    position_title = models.CharField(max_length=255)
    #department

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class EmployeeProfile(models.Model):
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    position_title = models.CharField(max_length=255, null=True, blank=True)

    # Validate these in form
    phone_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    phone_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)

    # status
    # skills

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


