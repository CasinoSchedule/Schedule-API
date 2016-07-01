from django.conf.urls import url, include
from schedules.views import WorkDayList, \
    ScheduleDetail, WorkDayDetail, EmployeeShiftsByMonth, \
    ListCreateShift, ShiftWeekList, ShiftCreateMany, ShiftRetrieveUpdateDelete, \
    ShiftCreateByDate, ShiftCreateManyByDate

urlpatterns = [
    url(r'^employeemonth/$', EmployeeShiftsByMonth.as_view(),
        name="days_by_month"),

    url(r'^shift/(?P<pk>\d+)/$', ShiftRetrieveUpdateDelete.as_view(),
        name="shift_retrieve_delete"),
    url(r'^shift/date/$', ShiftCreateByDate.as_view(), name="shift_create_by_date"),
    url(r'^shift/$', ListCreateShift.as_view(), name="list_create_shift"),

    url(r'^manyshift/$', ShiftCreateMany.as_view(), name="shift_create_many"),
    url(r'^manyshiftdate/$', ShiftCreateManyByDate.as_view(), name="multiple_shift_by_date"),

    url(r'^weekshift/$', ShiftWeekList.as_view(),
        name="schedule_shifts"),

    # url(r'^current/$', CurrentSchedules.as_view(), name="current_schedule"),
    url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name="schedule_detail"),

    # url(r'^bydate/$', ArbitraryDateSchedule.as_view(),
    #     name="schedule_by_date"),

    url(r'^workday/$', WorkDayList.as_view(), name="work_days"),
    url(r'^workday/(?P<pk>\d+)/$', WorkDayDetail.as_view(),
        name="workday_detail"),
]
