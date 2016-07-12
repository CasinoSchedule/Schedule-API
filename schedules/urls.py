from django.conf.urls import url, include
from schedules.views import WorkDayList, \
    ScheduleDetail, WorkDayDetail, EmployeeShiftsByMonth, \
    ListCreateShift, ShiftWeekList, ShiftRetrieveUpdateDelete, \
    ShiftCreateByDate, ShiftCreateManyByDate, CustomShift, ActivateShiftWeek, \
    RetrieveEOList, CreateEOEntry

urlpatterns = [
    url(r'^employeemonth/$', EmployeeShiftsByMonth.as_view(),
        name="days_by_month"),
    # url(r'^employee/month/$', EmployeeShiftsByMonthActual.as_view(),
    #     name="employee_month"),

    url(r'^shift/(?P<pk>\d+)/$', ShiftRetrieveUpdateDelete.as_view(),
        name="shift_retrieve_delete"),
    url(r'^shift/date/$', ShiftCreateByDate.as_view(), name="shift_create_by_date"),
    url(r'^shift/$', ListCreateShift.as_view(), name="list_create_shift"),
    #url(r'^custom/$', CustomShift.as_view(), name="custom_shift"),

    # url(r'^manyshift/$', ShiftCreateMany.as_view(), name="shift_create_many"),
    url(r'^shift/many/$', ShiftCreateManyByDate.as_view(), name="multiple_shift_by_date"),
    url(r'^shift/publish/$', ActivateShiftWeek.as_view(), name='publish_shift_week'),

    url(r'^weekshift/$', ShiftWeekList.as_view(),
        name="schedule_shifts"),

    # url(r'^current/$', CurrentSchedules.as_view(), name="current_schedule"),
    url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name="schedule_detail"),

    # url(r'^bydate/$', ArbitraryDateSchedule.as_view(),
    #     name="schedule_by_date"),

    url(r'^workday/$', WorkDayList.as_view(), name="work_days"),
    url(r'^workday/(?P<pk>\d+)/$', WorkDayDetail.as_view(),
        name="workday_detail"),

    url(r'^eolist/retrieve/$', RetrieveEOList.as_view(), name='retrieve_eo_list'),
    url(r'^eolist/entry/$', CreateEOEntry.as_view(),
        name='create_eo_entry'),

]
