from django.conf.urls import url

from profiles.views import EmployeeProfileListCreateView, ProfileCheck, \
    EmployeeProfileGetDelete, EmployeeProfileUpdate, UserCreateWithEmployeeProfile, \
    UserList, NotifyNewEmployee, MessageEmployees

urlpatterns = [
    url(r'^employee/$', EmployeeProfileListCreateView.as_view(),
        name="employee_list_create"),
    url(r'^employee/update/(?P<pk>\d+)/$', EmployeeProfileUpdate.as_view(),
        name="employee_update"),
    url(r'^employee/(?P<pk>\d+)/$',
        EmployeeProfileGetDelete.as_view(),
        name="employee_update_delete"),

    url(r'^check/$', ProfileCheck.as_view(),
        name="profile_check"),

    url(r'^useremployee/$', UserCreateWithEmployeeProfile.as_view(),
        name="user_with_profile"),

    url(r'^user/$', UserList.as_view(),
        name="user_list"),

    url(r'^notify/employee/$', NotifyNewEmployee.as_view(),
        name="notify_new_employee"),

    url(r'^message/everyone/$', MessageEmployees.as_view(),
        name="message_employees"),
]