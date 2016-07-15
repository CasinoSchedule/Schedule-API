from django.conf.urls import url

from profiles.views import EmployeeProfileListCreateView, ProfileCheck, \
    EmployeeProfileGetDelete, EmployeeProfileUpdate

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

]