# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-16 14:31
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import base.models.learning_unit_year


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0389_auto_20181114_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationgroupachievement',
            options={'ordering': ('order',), 'verbose_name': 'Education group achievement'},
        ),
        migrations.AlterModelOptions(
            name='educationgroupdetailedachievement',
            options={'ordering': ('order',), 'verbose_name': 'Education group detailed achievement'},
        ),
        migrations.AlterModelOptions(
            name='educationgroupyear',
            options={'verbose_name': 'Education group year'},
        ),
        migrations.AlterField(
            model_name='academiccalendar',
            name='reference',
            field=models.CharField(choices=[('DELIBERATION', 'Deliberation'), ('DISSERTATION_SUBMISSION', 'Dissertation submission'), ('EXAM_ENROLLMENTS', 'Exam enrollments'), ('SCORES_EXAM_DIFFUSION', 'Scores exam diffusion'), ('SCORES_EXAM_SUBMISSION', 'Scores exam submission'), ('TEACHING_CHARGE_APPLICATION', 'Teaching charge application'), ('COURSE_ENROLLMENT', 'Course enrollment'), ('SUMMARY_COURSE_SUBMISSION', 'Summary course submission'), ('EDUCATION_GROUP_EDITION', 'Education group edition'), ('EDITION_OF_GENERAL_INFORMATION', 'Edition of general information'), ('TESTING', 'Testing'), ('RELEASE', 'Release')], max_length=50),
        ),
        migrations.AlterField(
            model_name='certificateaim',
            name='description',
            field=models.CharField(db_index=True, max_length=1024, unique=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='educationgroup',
            name='start_year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Start'),
        ),
        migrations.AlterField(
            model_name='educationgroupachievement',
            name='education_group_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear', verbose_name='Education group year'),
        ),
        migrations.AlterField(
            model_name='educationgroupdetailedachievement',
            name='education_group_achievement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupAchievement', verbose_name='Education group achievement'),
        ),
        migrations.AlterField(
            model_name='educationgrouporganization',
            name='all_students',
            field=models.BooleanField(default=False, verbose_name='For all students'),
        ),
        migrations.AlterField(
            model_name='educationgrouporganization',
            name='diploma',
            field=models.CharField(choices=[('UNIQUE', 'Unique'), ('SEPARATE', 'Separate'), ('NOT_CONCERNED', 'Not concerned')], default='NOT_CONCERNED', max_length=40, verbose_name='UCL Diploma'),
        ),
        migrations.AlterField(
            model_name='educationgrouptype',
            name='category',
            field=models.CharField(choices=[('TRAINING', 'Training'), ('MINI_TRAINING', 'Mini-Training'), ('GROUP', 'Group')], default='TRAINING', max_length=25, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='educationgrouptype',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Type of training'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='academic_type',
            field=models.CharField(blank=True, choices=[('NON_ACADEMIC', 'Non academic'), ('NON_ACADEMIC_CREF', 'Non academic CREF'), ('ACADEMIC', 'Academic')], max_length=20, null=True, verbose_name='Academic type'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='acronym',
            field=models.CharField(db_index=True, max_length=40, verbose_name='Acronym'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='active',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('RE_REGISTRATION', 'Reregistration')], default='ACTIVE', max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='administration_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='administration_entity', to='base.Entity', verbose_name='Administration entity'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='admission_exam',
            field=models.BooleanField(default=False, verbose_name='Admission exam'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='diploma_printing_orientation',
            field=models.CharField(blank=True, choices=[('NO_PRINT', 'No print'), ('IN_HEADING_2_OF_DIPLOMA', 'In heading 2 of diploma'), ('IN_EXPECTED_FORM', 'In expected form')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='diploma_printing_title',
            field=models.CharField(blank=True, default='', max_length=140, verbose_name='Diploma title'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='duration',
            field=models.IntegerField(blank=True, default=1, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Duration'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='duration_unit',
            field=models.CharField(blank=True, choices=[('QUADRIMESTER', 'Quadrimester'), ('TRIMESTER', 'Trimester'), ('MONTH', 'Month'), ('WEEK', 'Week'), ('DAY', 'Day')], default='QUADRIMESTER', max_length=40, null=True, verbose_name='duration unit'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='education_group_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupType', verbose_name='Type of training'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='english_activities',
            field=models.CharField(blank=True, choices=[('YES', 'yes'), ('NO', 'no'), ('OPTIONAL', 'optional')], max_length=20, null=True, verbose_name='activities in English'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='enrollment_campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollment', to='base.Campus', verbose_name='Enrollment campus'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='enrollment_enabled',
            field=models.BooleanField(default=True, verbose_name='Enrollment enabled'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding',
            field=models.BooleanField(default=False, verbose_name='Funding'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding_cud',
            field=models.BooleanField(default=False, verbose_name='Funding international cooperation CCD/CUD'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding_direction',
            field=models.CharField(blank=True, default='', max_length=1, verbose_name='Funding direction'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding_direction_cud',
            field=models.CharField(blank=True, default='', max_length=1, verbose_name='Funding international cooperation CCD/CUD direction'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='internship',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no'), ('OPTIONAL', 'optional')], default='NO', max_length=20, null=True, verbose_name='Internship'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='joint_diploma',
            field=models.BooleanField(default=False, verbose_name='University certificate'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='keywords',
            field=models.CharField(blank=True, default='', max_length=320, verbose_name='Keywords'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='main_teaching_campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teaching', to='base.Campus', verbose_name='Learning location'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='management_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='management_entity', to='base.Entity', verbose_name='Management entity'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='other_campus_activities',
            field=models.CharField(blank=True, choices=[('YES', 'yes'), ('NO', 'no'), ('OPTIONAL', 'optional')], max_length=20, null=True, verbose_name='Other languages activities'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='other_language_activities',
            field=models.CharField(blank=True, choices=[('YES', 'yes'), ('NO', 'no'), ('OPTIONAL', 'optional')], max_length=20, null=True, verbose_name='Other languages activities'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='partial_deliberation',
            field=models.BooleanField(default=False, verbose_name='Partial deliberation'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='primary_language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Language', verbose_name='Primary language'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='professional_title',
            field=models.CharField(blank=True, default='', max_length=320, verbose_name='Professionnal title'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='rate_code',
            field=models.CharField(blank=True, choices=[('NO_ADDITIONAL_FEES', 'No additional fees'), ('AESS_CAPAES', 'AESS CAPAES'), ('MINERVAL_COMPLETE', 'Minerval complete'), ('UNIVERSITY_CERTIFICATE', 'University certificate'), ('ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION', 'Advanced master in medical specialization'), ('ACCESS_CONTEST', 'Access contest'), ('UNIVERSITY_CERTIFICATE_30_CREDITS', 'University certificate 30 credits'), ('CERTIFICATE_MEDECINE_COMPETENCE', 'Certificate medicine competence')], max_length=50, null=True, verbose_name='Rate code'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='remark_english',
            field=models.TextField(blank=True, default='', verbose_name='remark in english'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='schedule_type',
            field=models.CharField(choices=[('DAILY', 'Daily'), ('SHIFTED', 'Shifted'), ('ADAPTED', 'Adapted')], default='DAILY', max_length=20, verbose_name='Schedule type'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Title in French'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='title_english',
            field=models.CharField(blank=True, default='', max_length=240, verbose_name='Title in English'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='university_certificate',
            field=models.BooleanField(default=False, verbose_name='University certificate'),
        ),
        migrations.AlterField(
            model_name='entitycontaineryear',
            name='type',
            field=models.CharField(choices=[('REQUIREMENT_ENTITY', 'Requirement entity'), ('ALLOCATION_ENTITY', 'Allocation entity'), ('ADDITIONAL_REQUIREMENT_ENTITY_1', 'Additional requirement entity 1'), ('ADDITIONAL_REQUIREMENT_ENTITY_2', 'Additional requirement entity 2')], max_length=35),
        ),
        migrations.AlterField(
            model_name='entityversion',
            name='entity_type',
            field=models.CharField(blank=True, choices=[('SECTOR', 'Sector'), ('FACULTY', 'Faculty'), ('SCHOOL', 'School'), ('INSTITUTE', 'Institute'), ('POLE', 'Pole'), ('DOCTORAL_COMMISSION', 'Doctoral commission'), ('PLATFORM', 'Platform'), ('LOGISTICS_ENTITY', 'Logistics entity')], db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='enrollment_state',
            field=models.CharField(choices=[('ENROLLED', 'Enrolled'), ('NOT_ENROLLED', 'Not enrolled')], db_index=True, default='ENROLLED', max_length=20),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_draft',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'Absence unjustified'), ('ABSENCE_JUSTIFIED', 'Absence justified'), ('CHEATING', 'Cheating')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_final',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'Absence unjustified'), ('ABSENCE_JUSTIFIED', 'Absence justified'), ('CHEATING', 'Cheating')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_reencoded',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'Absence unjustified'), ('ABSENCE_JUSTIFIED', 'Absence justified'), ('CHEATING', 'Cheating')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_draft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les scores doivent être compris entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les scores doivent être compris entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_final',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les scores doivent être compris entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les scores doivent être compris entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_reencoded',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les scores doivent être compris entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les scores doivent être compris entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollmenthistory',
            name='justification_final',
            field=models.CharField(choices=[('ABSENCE_UNJUSTIFIED', 'Absence unjustified'), ('ABSENCE_JUSTIFIED', 'Absence justified'), ('CHEATING', 'Cheating')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='externallearningunityear',
            name='external_acronym',
            field=models.CharField(blank=True, db_index=True, max_length=15, verbose_name='External code'),
        ),
        migrations.AlterField(
            model_name='externallearningunityear',
            name='external_credits',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(500)], verbose_name='Local credits'),
        ),
        migrations.AlterField(
            model_name='externallearningunityear',
            name='requesting_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Entity', verbose_name='Requesting entity'),
        ),
        migrations.AlterField(
            model_name='externallearningunityear',
            name='url',
            field=models.URLField(blank=True, max_length=255, verbose_name='URL of the learning unit'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='block',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='Block'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='is_mandatory',
            field=models.BooleanField(default=False, verbose_name='Mandatory'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='link_type',
            field=models.CharField(blank=True, choices=[('REFERENCE', 'Reference')], max_length=25, null=True, verbose_name='Link type'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='max_credits',
            field=models.IntegerField(blank=True, null=True, verbose_name='Max. credits'),
        ),
        migrations.AlterField(
            model_name='groupelementyear',
            name='min_credits',
            field=models.IntegerField(blank=True, null=True, verbose_name='Min. credits'),
        ),
        migrations.AlterField(
            model_name='learningachievement',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Language', verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='learningcomponentyear',
            name='type',
            field=models.CharField(blank=True, choices=[('LECTURING', 'Lecturing'), ('PRACTICAL_EXERCISES', 'Practical exercises')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='common_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Common title'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='common_title_english',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Common English title'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='container_type',
            field=models.CharField(choices=[('COURSE', 'Course'), ('INTERNSHIP', 'Internship'), ('DISSERTATION', 'Dissertation'), ('OTHER_COLLECTIVE', 'Other collective'), ('OTHER_INDIVIDUAL', 'Other individual'), ('MASTER_THESIS', 'Master thesis'), ('EXTERNAL', 'External')], max_length=20, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='is_vacant',
            field=models.BooleanField(default=False, verbose_name='Vacant'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='team',
            field=models.BooleanField(default=False, verbose_name='Team management'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='type_declaration_vacant',
            field=models.CharField(blank=True, choices=[('RESEVED_FOR_INTERNS', 'Reserved for interns'), ('OPEN_FOR_EXTERNS', 'Open for externs'), ('EXCEPTIONAL_PROCEDURE', 'Exceptional procedure'), ('VACANT_NOT_PUBLISH', 'Vacant not publish'), ('DO_NOT_ASSIGN', 'Do not assign')], max_length=100, null=True, verbose_name='Decision'),
        ),
        migrations.AlterField(
            model_name='learningunit',
            name='end_year',
            field=models.IntegerField(blank=True, null=True, verbose_name='End year'),
        ),
        migrations.AlterField(
            model_name='learningunit',
            name='faculty_remark',
            field=models.TextField(blank=True, null=True, verbose_name='Faculty remark'),
        ),
        migrations.AlterField(
            model_name='learningunit',
            name='other_remark',
            field=models.TextField(blank=True, null=True, verbose_name='Other remark'),
        ),
        migrations.AlterField(
            model_name='learningunit',
            name='start_year',
            field=models.IntegerField(verbose_name='Starting year'),
        ),
        migrations.AlterField(
            model_name='learningunitcomponent',
            name='type',
            field=models.CharField(blank=True, choices=[('LECTURING', 'Lecturing'), ('PRACTICAL_EXERCISES', 'Practical exercises')], db_index=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='learningunitenrollment',
            name='enrollment_state',
            field=models.CharField(choices=[('ENROLLED', 'Enrolled')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.AcademicYear', validators=[base.models.learning_unit_year.academic_year_validator], verbose_name='Academic year'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='attribution_procedure',
            field=models.CharField(blank=True, choices=[('INTERNAL_TEAM', 'Internal team'), ('EXTERNAL', 'External')], max_length=20, null=True, verbose_name='Procedure'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='campus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Campus', verbose_name='Learning location'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='internship_subtype',
            field=models.CharField(blank=True, choices=[('TEACHING_INTERNSHIP', 'Teaching internship'), ('CLINICAL_INTERNSHIP', 'Clinical internship'), ('PROFESSIONAL_INTERNSHIP', 'Professional internship'), ('RESEARCH_INTERNSHIP', 'Research internship')], max_length=250, null=True, verbose_name='Internship subtype'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Language', verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='periodicity',
            field=models.CharField(choices=[('ANNUAL', 'Annual'), ('BIENNIAL_EVEN', 'biennial even'), ('BIENNIAL_ODD', 'biennial odd')], default='ANNUAL', max_length=20, verbose_name='Periodicity'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='professional_integration',
            field=models.BooleanField(default=False, verbose_name='professional integration'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='quadrimester',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q1 and Q2', 'Q1 and Q2'), ('Q1 or Q2', 'Q1 or Q2'), ('Q3', 'Q3')], max_length=9, null=True, verbose_name='Quadrimester'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='session',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('12', '12'), ('13', '13'), ('23', '23'), ('123', '123'), ('P23', 'P23')], max_length=50, null=True, verbose_name='Session derogation'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='specific_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='English title proper'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='specific_title_english',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='English title proper'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='status',
            field=models.BooleanField(default=False, verbose_name='Active'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='subtype',
            field=models.CharField(choices=[('FULL', 'Full'), ('PARTIM', 'Partim')], default='FULL', max_length=50),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='summary_locked',
            field=models.BooleanField(default=False, verbose_name='blocked update for tutor'),
        ),
        migrations.AlterField(
            model_name='mandate',
            name='function',
            field=models.CharField(choices=[('PRESIDENT', 'President'), ('SECRETARY', 'Secretary'), ('SIGNATORY', 'Signatory')], max_length=20),
        ),
        migrations.AlterField(
            model_name='offerenrollment',
            name='enrollment_state',
            field=models.CharField(blank=True, choices=[('SUBSCRIBED', 'Subscribed'), ('PROVISORY', 'Provisory'), ('PENDING', 'Pending'), ('TERMINATION', 'Termination'), ('END_OF_CYCLE', 'End of cycle')], max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='offeryear',
            name='grade',
            field=models.CharField(blank=True, choices=[('BACHELOR', 'bachelor'), ('MASTER', 'Master'), ('DOCTORATE', 'Ph.D')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='offeryearentity',
            name='type',
            field=models.CharField(blank=True, choices=[('ENTITY_ADMINISTRATION', 'Administration entity'), ('ENTITY_MANAGEMENT', 'Management entity')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.CharField(blank=True, choices=[('MAIN', 'Main'), ('ACADEMIC_PARTNER', 'Academic partner'), ('INDUSTRIAL_PARTNER', 'Industrial partner'), ('SERVICE_PARTNER', 'Service partner'), ('COMMERCE_PARTNER', 'Commerce partner'), ('PUBLIC_PARTNER', 'Public partner')], default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(blank=True, choices=[('F', 'Female'), ('M', 'Male'), ('U', 'unknown')], default='U', max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='source',
            field=models.CharField(blank=True, choices=[('BASE', 'Base'), ('DISSERTATION', 'Dissertation')], default='BASE', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='prerequisite',
            name='main_operator',
            field=models.CharField(choices=[('OR', 'Or'), ('AND', 'And')], default='AND', max_length=5),
        ),
        migrations.AlterField(
            model_name='proposallearningunit',
            name='state',
            field=models.CharField(choices=[('FACULTY', 'Faculty'), ('CENTRAL', 'Central'), ('SUSPENDED', 'Suspended'), ('ACCEPTED', 'Accepted'), ('REFUSED', 'Refused')], default='FACULTY', max_length=50, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='proposallearningunit',
            name='type',
            field=models.CharField(choices=[('CREATION', 'Creation'), ('MODIFICATION', 'Modification'), ('TRANSFORMATION', 'Transformation'), ('TRANSFORMATION_AND_MODIFICATION', 'Transformation and modification'), ('SUPPRESSION', 'Suppression')], default='MODIFICATION', max_length=50, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='structure',
            name='type',
            field=models.CharField(blank=True, choices=[('SECTOR', 'Sector'), ('FACULTY', 'Faculty'), ('INSTITUTE', 'Institute'), ('POLE', 'Pole'), ('DOCTORAL_COMMISSION', 'Doctoral commission'), ('PROGRAM_COMMISSION', 'Program commission'), ('LOGISTIC', 'Logistic'), ('RESEARCH_CENTER', 'Research center'), ('TECHNOLOGIC_PLATFORM', 'Technologic platform'), ('UNDEFINED', 'Undefined')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='validationrule',
            name='status_field',
            field=models.CharField(choices=[('REQUIRED', 'Required'), ('FIXED', 'Fixed'), ('ALERT', 'Alert'), ('NOT_REQUIRED', 'Not required'), ('DISABLED', 'Disabled')], default='NOT_REQUIRED', max_length=20),
        ),
    ]
