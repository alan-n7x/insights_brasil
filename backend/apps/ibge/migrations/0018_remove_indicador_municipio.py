# Generated migration to remove IndicadorMunicipio model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ibge', '0017_migrate_to_fato_indicador'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IndicadorMunicipio',
        ),
    ]
