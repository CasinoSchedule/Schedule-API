from django.conf.urls import url

from profiles.views import EmployeeProfileListCreateView, ProfileCheck

urlpatterns = [
    url(r'^employee/$', EmployeeProfileListCreateView.as_view(),
        name="employee_list"),
    url(r'^check/$', ProfileCheck.as_view(),
        name="profile_check"),

]