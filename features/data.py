from behave.runner import Context

from features import factories as functional_factories
from features.factories import academic_year, reference, structure, users, score_encoding, learning_unit, \
    education_group
from features.factories.attribution import AttributionGenerator


def setup_data(context: Context):
    data = {}
    academic_year_factory = functional_factories.academic_year.AcademicYearGenerator()
    data["current_academic_year"] = academic_year_factory.current_academic_year
    context.current_academic_year = functional_factories.academic_year.AcademicYearGenerator().current_academic_year

    functional_factories.reference.ReferenceDataGenerator()
    functional_factories.structure.EntityVersionTreeGenerator()
    functional_factories.structure.CampusGenerator()
    context.users = functional_factories.users.UsersGenerator()
    functional_factories.score_encoding.ScoreEncodingFactory()
    context.setup_data = functional_factories.learning_unit.LearningUnitGenerator()
    functional_factories.education_group.OfferBusinessFactory()

    return context


def setup_data_bis():
    data = {}
    academic_year_factory = functional_factories.academic_year.AcademicYearGenerator()
    data["current_academic_year"] = academic_year_factory.current_academic_year
    current_academic_year = functional_factories.academic_year.AcademicYearGenerator().current_academic_year

    functional_factories.reference.ReferenceDataGenerator()
    functional_factories.structure.StructureGenerator()
    users = functional_factories.users.UsersGenerator()
    setup_data = functional_factories.learning_unit.LearningUnitGenerator()
    AttributionGenerator()
    functional_factories.score_encoding.ScoreEncodingFactory()
    functional_factories.education_group.OfferBusinessFactory()

    return None
