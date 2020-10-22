##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path

import base.views.education_groups.create
import base.views.learning_units.common
import base.views.learning_units.create
import base.views.learning_units.delete
import base.views.learning_units.proposal.consolidate
import base.views.learning_units.proposal.delete
import base.views.learning_units.search.borrowed
import base.views.learning_units.search.educational_information
import base.views.learning_units.search.external
import base.views.learning_units.search.proposal
import base.views.learning_units.search.service_course
import base.views.learning_units.search.simple
import base.views.learning_units.update
from attribution.views import attribution, tutor_application
from base.views import learning_achievement, search, user_list
from base.views import learning_unit, offer, common, institution, organization, academic_calendar, \
    my_osis, entity, student, notifications
from base.views import teaching_material
from base.views.education_groups import urls as education_groups_urls
from base.views.filter import filter_cities_by_country, filter_campus_by_city
from base.views.learning_units.detail import DetailLearningUnitYearView
from base.views.learning_units.external import create as create_external
from base.views.learning_units.pedagogy.publish import publish_and_access_publication
from base.views.learning_units.pedagogy.read import learning_unit_pedagogy
from base.views.learning_units.pedagogy.update import learning_unit_pedagogy_edit, toggle_summary_locked, \
    learning_unit_pedagogy_force_majeure_edit
from base.views.learning_units.proposal import create, update
from base.views.learning_units.update import update_learning_unit, learning_unit_edition_end_date
from base.views.organization import OrganizationAutocomplete, CountryAutocomplete, CampusAutocomplete
from base.views.person import EmployeeAutocomplete

urlpatterns = [
    url(r'^$', common.home, name='home'),
    url(
        r'^entity_autocomplete/$',
        base.views.learning_units.update.EntityAutocomplete.as_view(),
        name='entity_autocomplete'
    ),
    url(
        r'^allocation_entity_autocomplete/$',
        base.views.learning_units.update.AllocationEntityAutocomplete.as_view(),
        name='allocation_entity_autocomplete'
    ),
    url(
        r'^additional_entity_1_autocomplete/$',
        base.views.learning_units.update.AdditionnalEntity1Autocomplete.as_view(),
        name='additional_entity_1_autocomplete'
    ),
    url(
        r'^additional_entity_2_autocomplete/$',
        base.views.learning_units.update.AdditionnalEntity2Autocomplete.as_view(),
        name='additional_entity_2_autocomplete'
    ),
    url(
        r'^entity_requirement_autocomplete/$',
        base.views.learning_units.update.EntityRequirementAutocomplete.as_view(),
        name='entity_requirement_autocomplete'
    ),
    url(r'^organization-autocomplete/$', OrganizationAutocomplete.as_view(),
        name='organization_autocomplete'),
    url(r'^country-autocomplete/$', CountryAutocomplete.as_view(),
        name='country-autocomplete'),
    url(r'^campus-autocomplete/$', CampusAutocomplete.as_view(),
        name='campus-autocomplete'),
    url(r'^employee-autocomplete/$', EmployeeAutocomplete.as_view(),
        name='employee_autocomplete'),
    url(r'^list-of-users/$', user_list.UserListView.as_view(), name='academic_actors_list'),

    url(r'^academic_actors/', include([
        url(r'^$', institution.academic_actors, name='academic_actors'),
    ])),

    url(r'^academic_calendars/', include([
        url(r'^$', academic_calendar.academic_calendars, name='academic_calendars'),
        url(r'^(?P<academic_calendar_id>[0-9]+)/$', academic_calendar.academic_calendar_read,
            name='academic_calendar_read'),
        url(r'^form(?:/(?P<academic_calendar_id>[0-9]+))?/$', academic_calendar.academic_calendar_form,
            name='academic_calendar_form'),
        url(r'^delete(?:/(?P<pk>[0-9]+))?/$', academic_calendar.AcademicCalendarDelete.as_view(),
            name='academic_calendar_delete'),
    ])),

    url(r'^admin/', include([
        url(r'^data/$', common.data, name='data'),
        url(r'^data/maintenance$', common.data_maintenance, name='data_maintenance'),
        url(r'^storage/$', common.storage, name='storage'),
    ])),

    url(r'^api/v1/', include([
        url(r'^entities/$', entity.post_entities, name='post_entities'),
        url(r'^tutor_application/recompute_portal$', tutor_application.recompute_portal,
            name='recompute_tutor_application_portal'),
        url(r'^attribution/recompute_portal$', attribution.recompute_portal, name='recompute_attribution_portal'),
    ])),

    url(r'^catalog/$', common.catalog, name='catalog'),

    url(r'^entities/', include([
        url(r'^$', institution.entities_search, name='entities'),
        url(r'^(?P<entity_version_id>[0-9]+)/', include([
            url(r'^$', institution.entity_read, name='entity_read'),
            url(r'^address/$', institution.get_entity_address, name='entity_address'),
            url(r'^diagram/$', institution.entity_diagram, name='entity_diagram'),
            url(r'^versions/$', institution.entities_version, name='entities_version'),
        ]))
    ])),

    url(r'^institution/', include([
        url(r'^$', institution.institution, name='institution'),
        url(r'^mandates/$', institution.mandates, name='mandates'),
    ])),

    url(r'^learning_units/', include([
        url(r'^by_activity/', base.views.learning_units.search.simple.LearningUnitSearch.as_view(),
            name='learning_units'),
        url(r'^by_service_course/', base.views.learning_units.search.service_course.ServiceCourseSearch.as_view(),
            name='learning_units_service_course'),
        url(r'^by_proposal/', base.views.learning_units.search.proposal.SearchLearningUnitProposal.as_view(),
            name='learning_units_proposal'),
        url(r'^by_borrowed_course/', base.views.learning_units.search.borrowed.BorrowedLearningUnitSearch.as_view(),
            name='learning_units_borrowed_course'),
        url(r'^by_summary/',
            base.views.learning_units.search.educational_information.LearningUnitDescriptionFicheSearch.as_view(),
            name='learning_units_summary'),
        url(r'^by_external/', base.views.learning_units.search.external.ExternalLearningUnitSearch.as_view(),
            name='learning_units_external'),
        url(r'^new/', include([
            url(r'^academic_year_id=(?P<academic_year_id>[0-9]+)$',
                base.views.learning_units.create.create_learning_unit,
                name="learning_unit_create"),
            url(r'^proposal/academic_year_id=(?P<academic_year>[0-9]+)$',
                create.get_proposal_learning_unit_creation_form,
                name="proposal_learning_unit_creation_form"),
            url(r'^external/academic_year_id=(?P<academic_year>[0-9]+)$',
                create_external.get_external_learning_unit_creation_form,
                name="learning_unit_create_external"),
            url(r'^filter_cities_by_country$', filter_cities_by_country, name="filter_cities_by_country"),
            url(r'^filter_campus_by_city$', filter_campus_by_city, name="filter_campus_by_city"),
        ])),
        path(
            "<str:code>/<int:year>/publish_and_access_publication",
            publish_and_access_publication,
            name="publish_and_access_learning_unit_pedagogy"
        ),
        url(r'^(?P<learning_unit_year_id>[0-9]+)/', include([
            url(r'^$', DetailLearningUnitYearView.as_view(), name='learning_unit'),
            url(r'^formations/$', learning_unit.learning_unit_formations, name="learning_unit_formations"),
            url(r'^components/$', learning_unit.learning_unit_components, name="learning_unit_components"),
            url(r'^pedagogy/', include([
                url(r'^$', learning_unit_pedagogy, name="learning_unit_pedagogy"),
                url(r'^edit/$', learning_unit_pedagogy_edit, name="learning_unit_pedagogy_edit"),
                url(
                    r'^edit_force_majeure/$',
                    learning_unit_pedagogy_force_majeure_edit,
                    name="learning_unit_pedagogy_force_majeure_edit"
                ),
                url(r'^toggle_summary_locked/$', toggle_summary_locked,
                    name="learning_unit_pedagogy_toggle_summary_locked")
            ])),
            url(r'^proposal/', include([
                url(r'^modification/$', update.learning_unit_modification_proposal,
                    name="learning_unit_modification_proposal"),
                url(r'^suppression/$', update.learning_unit_suppression_proposal,
                    name="learning_unit_suppression_proposal"),
                url(r'^edit/$', update.update_learning_unit_proposal, name="edit_proposal"),
                url(r'^cancel/$', base.views.learning_units.proposal.delete.cancel_proposal_of_learning_unit,
                    name="learning_unit_cancel_proposal"),
                url(r'^consolidate/$', base.views.learning_units.proposal.consolidate.consolidate_proposal,
                    name="learning_unit_consolidate_proposal"),
            ])),
            url(r'^update_end_date/$', learning_unit_edition_end_date, name="learning_unit_edition"),
            url(r'^update/$', update_learning_unit, name="edit_learning_unit"),
            url(r'^specifications/$', learning_unit.learning_unit_specifications, name="learning_unit_specifications"),
            url(r'^specifications/edit/$', learning_unit.learning_unit_specifications_edit,
                name="learning_unit_specifications_edit"),
            url(r'^volumes/(?P<form_type>[a-z]+)$', base.views.learning_units.update.learning_unit_volumes_management,
                name="learning_unit_volumes_management"),
            url(r'^delete_full/$', base.views.learning_units.delete.delete_all_learning_units_year,
                name="learning_unit_delete_all"),
            url(r'^partim/', include([
                url(r'^new/$', base.views.learning_units.create.create_partim_form, name="learning_unit_create_partim"),
            ])),
            url(r'^achievements/', include([
                url(r'^management/', learning_achievement.management, name="achievement_management"),
                url(r'^(?P<learning_achievement_id>[0-9]+)/edit/', learning_achievement.update,
                    name="achievement_edit"),
                url(r'^create/', learning_achievement.create_first,
                    name="achievement_create_first"),

                url(r'^(?P<learning_achievement_id>[0-9]+)/create/', learning_achievement.create,
                    name="achievement_create"),
                url(r'^check_code/', learning_achievement.check_code,
                    name="achievement_check_code"),

            ])),
            url(r'^teaching_materials/', include([
                url(r'^create', teaching_material.create, name="teaching_material_create"),
                url(r'^(?P<teaching_material_id>[0-9]+)/edit/', teaching_material.update,
                    name="teaching_material_edit"),
                url(r'^(?P<teaching_material_id>[0-9]+)/delete/', teaching_material.delete,
                    name="teaching_material_delete")
            ])),
            url(r'^comparison/$', learning_unit.learning_unit_comparison, name="learning_unit_comparison"),
            url(r'^proposal_comparison/$', learning_unit.learning_unit_proposal_comparison,
                name="learning_unit_proposal_comparison"),
            url(r'^consolidate/$', base.views.learning_units.proposal.consolidate.consolidate_proposal,
                name="learning_unit_consolidate_proposal"),
        ])),
        url(r'^check/(?P<subtype>[A-Z]+)$', base.views.learning_units.common.check_acronym, name="check_acronym"),
    ])),
    url(r'^proposals/search/$', base.views.learning_units.search.proposal.SearchLearningUnitProposal.as_view(),
        name="learning_unit_proposal_search"),

    url(r'^my_osis/', include([
        url(r'^$', my_osis.my_osis_index, name="my_osis"),
        url(r'^management_tasks/messages_templates', my_osis.messages_templates_index, name="messages_templates"),
        url(r'^my_messages/', include([
            url(r'^$', my_osis.my_messages_index, name="my_messages"),
            url(r'^action/$', my_osis.my_messages_action, name="my_messages_action"),
            url(r'^(?P<message_id>[0-9]+)/', include([
                url(r'^read/$', my_osis.read_message, name="read_my_message"),
                url(r'^delete/$', my_osis.delete_from_my_messages, name="delete_my_message"),
            ]))
        ])),
        url(r'^profile/', include([
            url(r'^$', my_osis.profile, name='profile'),
            url(r'^lang/$', my_osis.profile_lang, name='profile_lang'),
            url(r'^lang/edit/([A-Za-z-]+)/$', my_osis.profile_lang_edit, name='lang_edit'),
            url(r'^attributions/$', my_osis.profile_attributions, name='profile_attributions'),
        ]))
    ])),

    url(r'^noscript/$', common.noscript, name='noscript'),

    url(r'^offers/', include([
        url(r'^$', offer.offers, name='offers'),
        url(r'^search$', offer.offers_search, name='offers_search'),
    ])),

    url(r'^educationgroups/', include(education_groups_urls.urlpatterns)),

    url(r'^organizations/', include([
        url(r'^$', organization.OrganizationSearch.as_view(), name='organizations'),
        url(r'^search$', organization.OrganizationSearch.as_view(), name='organizations_search'),
        url(r'^(?P<organization_id>[0-9]+)/', include([
            url(r'^$', organization.DetailOrganization.as_view(), name='organization_read'),
        ])),
    ])),

    url(r'^organization_address/', include([
        url(r'^(?P<organization_address_id>[0-9]+)/', include([
            url(r'^read/$', organization.organization_address_read,
                name='organization_address_read'),
            url(r'^edit/$', organization.organization_address_edit,
                name='organization_address_edit'),
            url(r'^delete/$', organization.organization_address_delete,
                name='organization_address_delete')
        ]))
    ])),

    url(r'^search/', include([
        url(r'^tutors/$', search.search_tutors, name="search_tutors"),
    ])),

    url(r'^studies/$', common.studies, name='studies'),
    url(r'^students/', include([
        url(r'^$', student.students, name='students'),
        url(r'^(?P<student_id>[0-9]+)/', include([
            url(r'^$', student.student_read, name='student_read'),
            url(r'^picture$', student.student_picture, name='student_picture'),
        ]))
    ])),
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^clear_filter/$', base.views.search.clear_filter, name="clear_filter"),
    url(r'^notifications/', include([
        url(r'^clear/$', base.views.notifications.clear_user_notifications, name="clear_notifications"),
        url(r'^mark_as_read/$', base.views.notifications.mark_notifications_as_read, name="mark_notifications_as_read"),
    ])),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
