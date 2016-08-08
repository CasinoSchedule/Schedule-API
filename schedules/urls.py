from django.conf.urls import url
from schedules.views import WorkDayList, WorkDayDetail, EmployeeShiftsByMonth,\
    ShiftWeekList, ShiftCreateManyByDate, ActivateShiftWeek, \
    RetrieveEOList, CreateEOEntry, EOListList, CallOutListCreate, \
    TimeOffRequestCreate, TimeOffRequestList, AreaListCreate,\
    StationListCreate, AreaDetailUpdateDelete, AutoPopulateWeek, \
    ShiftTemplateListCreate, ShiftTemplateDetailUpdateDelete

urlpatterns = [
    url(r'^employeemonth/$', EmployeeShiftsByMonth.as_view(),
        name="days_by_month"),

    url(r'^shift/many/$', ShiftCreateManyByDate.as_view(),
        name="multiple_shift_by_date"),
    url(r'^shift/publish/$', ActivateShiftWeek.as_view(),
        name='publish_shift_week'),

    url(r'^weekshift/$', ShiftWeekList.as_view(),
        name="schedule_shifts"),

    url(r'^workday/$', WorkDayList.as_view(), name="work_days"),
    url(r'^workday/(?P<pk>\d+)/$', WorkDayDetail.as_view(),
        name="workday_detail"),

    url(r'^eolist/retrieve/$', RetrieveEOList.as_view(),
        name='retrieve_eo_list'),
    url(r'^eolist/entry/$', CreateEOEntry.as_view(),
        name='create_eo_entry'),
    url(r'^eolist/$', EOListList.as_view(), name='eo_lists'),

    url(r'^callout/$', CallOutListCreate.as_view(), name='callout_list'),
    url(r'^timeoff/create/$', TimeOffRequestCreate.as_view(),
        name='time_off_request_create'),
    url(r'^timeoff/list/$', TimeOffRequestList.as_view(),
        name='time_off_request_list'),

    url(r'^area/$', AreaListCreate.as_view(), name='area_list_create'),
    url(r'^area/(?P<pk>\d+)/$', AreaDetailUpdateDelete.as_view(),
        name='area_detail_update_delete'),
    url(r'^station/$', StationListCreate.as_view(),
        name='station_list_create'),

    url(r'^auto/$', AutoPopulateWeek.as_view(), name='auto_populate'),

    url(r'^shift/template/$', ShiftTemplateListCreate.as_view(),
        name='shift_template_list_create'),
    url(r'^shift/template/(?P<pk>\d+)/$',
        ShiftTemplateDetailUpdateDelete.as_view(),
        name='shift_template_detail')
]
