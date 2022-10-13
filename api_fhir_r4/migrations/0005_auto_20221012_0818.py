# Generated by Django 3.2.16 on 2022-10-12 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_fhir_r4', '0004_update_subscription_criteria'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalsubscription',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical subscription', 'verbose_name_plural': 'historical subscriptions'},
        ),
        migrations.AlterField(
            model_name='historicalsubscription',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]