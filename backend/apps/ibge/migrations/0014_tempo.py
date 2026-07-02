# Generated migration for Tempo model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ibge', '0013_remove_pibmunicipio_unique_pib_municipio_ano_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tempo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField(db_index=True)),
                ('mes', models.IntegerField(blank=True, db_index=True, help_text='1-12 para dados mensais', null=True)),
                ('trimestre', models.IntegerField(blank=True, db_index=True, help_text='1-4 para dados trimestrais', null=True)),
            ],
            options={
                'verbose_name': 'Tempo',
                'verbose_name_plural': 'Tempos',
                'ordering': ['-ano', '-mes', '-trimestre'],
            },
        ),
        migrations.AddConstraint(
            model_name='tempo',
            constraint=models.UniqueConstraint(fields=['ano', 'mes', 'trimestre'], name='uniq_tempo'),
        ),
    ]
