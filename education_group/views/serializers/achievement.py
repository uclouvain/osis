from base.models.education_group_achievement import EducationGroupAchievement
from program_management.ddd.domain.node import NodeGroupYear


def get_achievements(node: NodeGroupYear):
    qs = EducationGroupAchievement.objects.filter(
        education_group_year__educationgroupversion__root_group__partial_acronym=node.code,
        education_group_year__educationgroupversion__root_group__academic_year__year=node.year
    ).prefetch_related('educationgroupdetailedachievement_set')

    achievements = []
    for achievement in qs:
        achievements.append({
            **__get_achievement_formated(achievement),
            'detailed_achievements': [
                __get_achievement_formated(d_achievement) for d_achievement
                in achievement.educationgroupdetailedachievement_set.all()
            ]
        })
    return achievements


def __get_achievement_formated(achievement):
    return {'code_name': achievement.code_name, 'text_fr': achievement.french_text, 'text_en': achievement.english_text}
