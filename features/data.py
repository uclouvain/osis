from behave.runner import Context

from features import factories as functional_factories
from features.factories import academic_year, reference, structure, users, score_encoding, learning_unit, \
    education_group


def setup_data(context: Context):
    data = {}
    academic_year_factory = functional_factories.academic_year.BusinessAcademicYearFactory()
    data["current_academic_year"] = academic_year_factory.current_academic_year
    context.current_academic_year = functional_factories.academic_year.BusinessAcademicYearFactory().current_academic_year

    functional_factories.reference.BusinessLanguageFactory()
    functional_factories.structure.BusinessEntityVersionTreeFactory()
    functional_factories.structure.BusinessCampusFactory()
    functional_factories.users.BusinessUsersFactory()
    functional_factories.score_encoding.ScoreEncodingFactory()
    context.setup_data = functional_factories.learning_unit.LearningUnitBusinessFactory()
    functional_factories.education_group.OfferBusinessFactory()

    return context
