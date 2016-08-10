from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

import datetime

from profiles.models import EmployeeProfile


class EmployeeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user',
                                             password='pass_word')

    def test_detail_delete(self):
        self.employee = EmployeeProfile.objects.create(user=self.user,
                                                       first_name='john',
                                                       last_name='smith')
        url = reverse('employee_detail_delete', kwargs={'pk': self.employee.pk})
        response = self.client.get(url,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.employee.first_name)

