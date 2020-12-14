##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.urls import include, path, register_converter

from education_group.api.views.group import GroupDetail, GroupTitle
from education_group.api.views.group_element_year import TrainingTreeView, MiniTrainingTreeView, GroupTreeView
from education_group.api.views.hops import HopsList
from education_group.api.views.mini_training import MiniTrainingDetail, MiniTrainingTitle, MiniTrainingList, \
    OfferRoots
from education_group.api.views.training import TrainingList, TrainingDetail, TrainingTitle
from program_management.api.views.prerequisite import TrainingPrerequisites, MiniTrainingPrerequisites
from education_group.converters import AcronymConverter, TrainingAcronymConverter, MiniTrainingAcronymConverter

register_converter(AcronymConverter, 'mini_training_acronym')
register_converter(TrainingAcronymConverter, 'training_acronym')
register_converter(MiniTrainingAcronymConverter, 'mini_training_acronym')

app_name = "education_group"


urlpatterns = [
    path('hops/<int:year>', HopsList.as_view(), name=HopsList.name),
    path('trainings', TrainingList.as_view(), name=TrainingList.name),
    path('trainings/<int:year>/<training_acronym:acronym>/', include([
        path('tree', TrainingTreeView.as_view(), name=TrainingTreeView.name),
        path('title', TrainingTitle.as_view(), name=TrainingTitle.name),
        path('prerequisites', TrainingPrerequisites.as_view(), {'transition': False},
             name='{}_official'.format(TrainingPrerequisites.NAME)),
    ])),
    path(
        'trainings/<int:year>/<training_acronym:acronym>/versions/<str:version_name>',
        TrainingDetail.as_view(),
        name=TrainingDetail.name
    ),
    path(
        'trainings/<int:year>/<training_acronym:acronym>/versions/<str:version_name>/',
        include([
            path('tree', TrainingTreeView.as_view(), name=TrainingTreeView.name),
            path('title', TrainingTitle.as_view(), name=TrainingTitle.name),
        ])
    ),
    path(
        'trainings/<int:year>/<training_acronym:acronym>',
        TrainingDetail.as_view(),
        name=TrainingDetail.name
    ),
    path(
        'mini_trainings/<int:year>/<mini_training_acronym:acronym>/<str:version_name>)',
        MiniTrainingDetail.as_view(),
        name=MiniTrainingDetail.name
    ),
    path(
        'mini_trainings/<int:year>/<mini_training_acronym:acronym>/versions/<str:version_name>/',
        include([
            path('tree', MiniTrainingTreeView.as_view(), name=MiniTrainingTreeView.name),
            path('title', MiniTrainingTitle.as_view(), name=MiniTrainingTitle.name),
            path('offer_roots', OfferRoots.as_view(), name=OfferRoots.name),
        ])
    ),
    path('mini_trainings', MiniTrainingList.as_view(), name=MiniTrainingList.name),
    # TODO: Limit special characters authorized in mini trainings urls (in 4831)
    path('mini_trainings/<int:year>/<mini_training_acronym:acronym>/', include([
        path('tree', MiniTrainingTreeView.as_view(), name=MiniTrainingTreeView.name),
        path('title', MiniTrainingTitle.as_view(), name=MiniTrainingTitle.name),
        path('offer_roots', OfferRoots.as_view(), name=OfferRoots.name),
        path('prerequisites', MiniTrainingPrerequisites.as_view(), {'transition': False},
             name='{}_official'.format(MiniTrainingPrerequisites.NAME)),
    ])),
    path(
        'mini_trainings/<int:year>/<mini_training_acronym:acronym>',
        MiniTrainingDetail.as_view(),
        name=MiniTrainingDetail.name
    ),
    path(
        'groups/<int:year>/<str:partial_acronym>',
        GroupDetail.as_view(),
        name=GroupDetail.name
    ),
    path('groups/<int:year>/<str:partial_acronym>/', include([
        path('tree', GroupTreeView.as_view(), name=GroupTreeView.name),
        path('title', GroupTitle.as_view(), name=GroupTitle.name),
    ])),
]
