import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0489_auto_20191217_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningachievement',
            name='annual_id',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.RunSQL(
            sql=(
                'UPDATE base_learningachievement SET annual_id = CASE WHEN upper(code_name) = lower(code_name)'
                'THEN cast(code_name as int) ELSE 0 END;'
            ),
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
