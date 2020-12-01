from base import models as mdl
from base.utils import send_mail
from base.utils.send_mail import send_mail_after_scores_submission


def test(request):
    print('test')
    # pass
    # learning_unit_year = mdl.learning_unit_year.LearningUnitYear.objects.get(id=160652)
    learning_unit_year = mdl.learning_unit_year.LearningUnitYear.objects.get(id=206236)
    # offer_year = mdl.offer_year.OfferYear.objects.get(id=5599)
    offer_year = mdl.offer_year.OfferYear.objects.get(id=6069)
    enrollments = mdl.exam_enrollment.ExamEnrollment.objects.all()[:5]

    offer_acronym = offer_year.acronym
    # sent_error_message = None

    persons = list(set([tutor.person for tutor in mdl.tutor.find_by_learning_unit(learning_unit_year)]))
    for p in persons:
        p1 = p
        print("personne id  {} {} {}".format(p.id, p.language, p))
        break
    persons.append(mdl.person.find_by_id(132909))
    # send_mail.send_message_after_all_encoded_by_manager(persons, enrollments,
    #                                                                           learning_unit_year.acronym,
    #                                                                           offer_acronym)

    send_mail_after_scores_submission(persons, learning_unit_year.acronym, enrollments, True)
    return None
