from django.conf.urls import url, include
from schedules.views import CurrentSchedules, DayOfTheWeekList, WorkDayList, \
    ScheduleDetail, WorkDayDetail, EmployeeShiftsByMonth, \
    ListCreateShift

urlpatterns = [
    url(r'^employeemonth/$', EmployeeShiftsByMonth.as_view(),
        name="days_by_month"),

    url(r'shift/$', ListCreateShift.as_view(), name="list_create_shift"),

    url(r'^daysoftheweek/$', DayOfTheWeekList.as_view(),
        name="days_of_the_week"),
    url(r'^current/$', CurrentSchedules.as_view(), name="current_schedule"),
    url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name="schedule_detail"),

    # url(r'^bydate/$', ArbitraryDateSchedule.as_view(),
    #     name="schedule_by_date"),

    url(r'^workday/$', WorkDayList.as_view(), name="work_days"),
    url(r'^workday/(?P<pk>\d+)/$', WorkDayDetail.as_view(),
        name="workday_detail"),
]
