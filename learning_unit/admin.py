from django.contrib import admin

from learning_unit.models import learning_class_year

admin.site.register(learning_class_year.LearningClassYear,
                    learning_class_year.LearningClassYearAdmin)