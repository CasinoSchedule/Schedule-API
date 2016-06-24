from django.conf.urls import url, include
from schedules.views import CurrentSchedules, DayOfTheWeekList, WorkDayList, \
    ScheduleDetail, WorkDayDetail

urlpatterns = [
    url(r'^daysoftheweek/$', DayOfTheWeekList.as_view(),
        name="days_of_the_week"),
    url(r'^current/$', CurrentSchedules.as_view(), name="current_schedule"),
    url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name="schedule_detail"),
    url(r'^workday/$', WorkDayList.as_view(), name="work_days"),
    url(r'^workday/(?P<pk>\d+)/$', WorkDayDetail.as_view(),
        name="workday_detail"),
]
