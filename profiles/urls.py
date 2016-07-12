from django.conf.urls import url

from profiles.views import EmployeeProfileListCreateView, ProfileCheck, \
    EmployeeProfileGetUpdateDelete

urlpatterns = [
    url(r'^employee/$', EmployeeProfileListCreateView.as_view(),
        name="employee_list_create"),
    url(r'^employee/(?P<pk>\d+)/$',
        EmployeeProfileGetUpdateDelete.as_view(),
        name="employee_update_delete"),

    url(r'^check/$', ProfileCheck.as_view(),
        name="profile_check"),

]