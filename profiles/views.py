from django.contrib.auth.models import User
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from schedules.models import Shift
from schedules.permissions import IsManager
from schedules.sendgrid_functions import signup_email, general_email
from schedules.views import date_string_to_datetime

from profiles.models import EmployeeProfile, ManagerProfile
from profiles.serializers import EmployeeProfileSerializer, \
    UpdateCreateEmployeeProfileSerializer, UserCreateWithProfileSerializer,\
    UserSerializer

"""
Views for updating and creating profiles
"""


class NotifyNewEmployee(APIView):
    """
    POST an email and employee profile id. They will be sent a link to register
    as a new user, linked with that profile.
    example: {"email": "aaron@aol.com", "profile_id": 5}
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, format=None):
        employee = EmployeeProfile.objects.filter(
            id=request.data['profile_id']
        ).first()
        if not employee:
            return Response('No employee profile found',
                            status=status.HTTP_400_BAD_REQUEST)
        # if employee.was_invited:
        #     return Response('Employee already invited',
        #                     status=status.HTTP_400_BAD_REQUEST)

        signup_email(request.data['email'], request.data['profile_id'])
        employee.was_invited = True
        employee.save()
        return Response('email sent successfully', status=status.HTTP_200_OK)


class EmployeeProfileListCreateView(generics.ListCreateAPIView):
    """
    Use ?shift_title=1&department=1 to filter for employees on graveyard in
    department 1.
    """
    serializer_class = UpdateCreateEmployeeProfileSerializer
    permission_classes = (IsManager,)

    def get_queryset(self):
        qs = EmployeeProfile.objects.all().order_by('created_at')

        shift_title = self.request.query_params.get('shift_title')
        if shift_title:
            shift_title = [int(x) for x in shift_title.split(',')]
            qs = qs.filter(availability__in=shift_title)

        department = self.request.query_params.get('department')
        if department:
            qs = qs.filter(department=int(department))

        return qs


class EmployeeProfileGetDelete(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete an employee profile.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer


class EmployeeProfileUpdate(APIView):
    """
    Update employee profile.
    For days_off send a list of integers, 1=Monday, 7=Sunday.
    For availability send a list of integers, 1=grave, 2=day, 3=swing
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, pk):

        try:
            profile = EmployeeProfile.objects.get(pk=pk)
        except EmployeeProfile.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCreateEmployeeProfileSerializer(profile,
                                                           request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileCheck(APIView):
    """
    Takes a GET request with a token and returns an object with the type of
    profile the user has under 'type':
    Possible responses: {"type": "employee"}, {"type": "manager"},
     {"type": "no token"}, {"type": "no profile"}
    """

    def get(self, request, format=None):
        data = {}

        if not request.user.id:
            return Response({"type": "no token"})

        if EmployeeProfile.objects.filter(user=request.user).first():
            data['type'] = 'employee'
            data['department'] = request.user.employeeprofile.department_id
            data['department_title'] = request.user.employeeprofile.department.title
            return Response(data)
        elif ManagerProfile.objects.filter(user=request.user).first():
            data['type'] = 'manager'
            data['department'] = request.user.managerprofile.department_id
            data['department_title'] = request.user.managerprofile.department.title
            return Response(data)
        else:
            return Response({"type": "no profile"})


class UserCreateWithEmployeeProfile(APIView):
    """
    New user creation for those with an existing employee profile object.
    POST name, password, and employee profile_id.
    """

    def post(self, request, format=None):
        serializer = UserCreateWithProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployeeProfile.objects.filter(
                id=request.data['profile_id']
            ).first()

            if profile and profile.user:
                return Response("Profile already has a user",
                                status=status.HTTP_400_BAD_REQUEST
                                )
            serializer.save()
            profile.user = serializer.instance

            profile.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MessageEmployees(APIView):
    """
    POST email information to send to all employees in a department.
    example: {"department": 1, "subject": "test", "body": "blah"}
    """

    def post(self, request, format=None):
        subject = request.data['subject']
        body = request.data['body']
        employees = EmployeeProfile.objects.filter(
            department=request.data['department']
        )
        try:
            for employee in employees:
                if employee.email:
                    general_email(body=body,subject=subject,email=employee.email)
            return Response('emails sent', status=status.HTTP_200_OK)
        except:
            return Response('email error',
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)


class MessageAvailableEmployees(APIView):
    """
    Message all employees that are available to work a given time and date.
    For now an employee will be available if they do not have any other
    start times within 24 hours. We will add department and shift filters
    later.

    example: {"date": "2016-6-20", "time": "11:00", "department": 1}
    """

    def post(self, request, format=None):
        working_date = date_string_to_datetime(request.data['date'],
                                               request.data['time'])
        one_day = datetime.timedelta(days=1)
        after = working_date + one_day
        before = working_date - one_day

        qs = Shift.objects.filter(day__day_date__gte=before,
                                  day__day_date__lte=after)
        qs = qs.exclude(day__day_date=after,
                        starting_time__lte=working_date.time())
        qs = qs.exclude(day__day_date=before,
                        starting_time__gte=working_date.time())
        employees = qs.values('employee').distinct()
        employee_ids = [x['employee'] for x in employees]
        available_employees = EmployeeProfile.objects.filter(department=request.data['department'])
        available_employees = available_employees.exclude(id__in=employee_ids)
        try:
            subject = 'Shift available'
            body = 'There is a new shift available on {} at {}. If you would ' \
                   'like to work please contact your manager.'.format(
                request.data['date'], request.data['time'])
            for employee in available_employees:
                if employee.email:
                    general_email(body=body, subject=subject,
                                  email=employee.email)
            return Response('emails sent', status=status.HTTP_200_OK)
        except:
            return Response('email failed',
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
