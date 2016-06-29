from django.conf.urls import url

from profiles.views import EmployeeProfileListCreateView

urlpatterns = [
    url(r'^employee/$', EmployeeProfileListCreateView.as_view(),
        name="employee_list")

]