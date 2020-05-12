from django.urls import include, path

from education_group.views import group, training, mini_training

urlpatterns = [
    path('groups/<int:year>/<str:code>/', include([
        path('identification/', group.GroupReadIdentification.as_view(), name='group_identification'),
        path('content/', group.GroupReadContent.as_view(), name='group_content'),
        path('utilization/', group.GroupReadUtilization.as_view(), name='group_utilization'),
        path('general_information/', group.GroupReadGeneralInformation.as_view(), name='group_general_information'),
    ])),

    path('mini_trainings/<int:year>/<str:code>/', include([
        path(
            'identification/',
            mini_training.MiniTrainingReadIdentification.as_view(),
            name='mini_training_identification'
        ),
        path('content/', mini_training.MiniTrainingReadContent.as_view(), name='mini_training_content'),
        path('utilization/', mini_training.MiniTrainingReadUtilization.as_view(), name='mini_training_utilization'),
        path(
            'general_information/',
            mini_training.MiniTrainingReadGeneralInformation.as_view(),
            name='mini_training_general_information'
        ),
        path(
            'skills_achievements/',
            mini_training.MiniTrainingReadSkillsAchievements.as_view(),
            name='mini_training_skills_achievements'
        ),
        path(
            'admission_conditions/',
            mini_training.MiniTrainingReadAdmissionCondition.as_view(),
            name='mini_training_admission_condition'
        ),
    ])),
    path('trainings/<int:year>/<str:code>/', include([
        path('identification/', training.TrainingReadIdentification.as_view(), name='training_identification'),
        path('diplomas/', training.TrainingReadDiplomaCertificate.as_view(), name='training_diplomas'),
        path('content/', training.TrainingReadContent.as_view(), name='training_content'),
        path('utilization/', training.TrainingReadUtilization.as_view(), name='training_utilization'),
        path(
            'general_information/',
            training.TrainingReadGeneralInformation.as_view(),
            name='training_general_information'
        ),
        path(
            'skills_achievements/',
            training.TrainingReadSkillsAchievements.as_view(),
            name='training_skills_achievements'
        ),
        path(
            'admission_conditions/',
            training.TrainingReadAdmissionCondition.as_view(),
            name='training_admission_condition'
        ),
    ])),
    path('<int:year>/<str:code>/publish',
         group.GroupReadGeneralInformation.as_view(),
         name='publish_general_information')
]
