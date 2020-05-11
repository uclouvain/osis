from django.urls import include, path

from education_group.views import group_read

urlpatterns = [
    path('groups/<int:year>/<str:code>/', include([
        path('identification/', group_read.GroupReadIdentification.as_view(), name='group_identification'),
        path('content/', group_read.GroupReadContent.as_view(), name='group_content'),
        path('utilization/', group_read.GroupReadUsing.as_view(), name='group_utilization'),
        path('general_information/',
             group_read.GroupReadGeneralInformation.as_view(),
             name='group_general_information'),
        path('general_information/publish',
             group_read.GroupReadGeneralInformation.as_view(),
             name='publish_general_information')
    ])),
]
