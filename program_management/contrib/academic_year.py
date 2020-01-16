from base.models.academic_year import AcademicYear
from program_management.contrib.mixins import FetchedBusinessObject


class AcademicYearBusiness(FetchedBusinessObject):
    map_with_database = {
        AcademicYear: {
            'academic_year_id': 'id',
            'year': 'year',
        },
    }

    main_queryset_model_class = AcademicYear
