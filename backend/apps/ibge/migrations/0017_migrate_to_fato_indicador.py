# Data migration from IndicadorMunicipio to FatoIndicador

from django.db import migrations


def migrate_indicador_municipio_to_fato(apps, schema_editor):
    """
    Migrate data from IndicadorMunicipio to FatoIndicador.
    Creates Tempo records for each unique year and migrates all data.
    """
    IndicadorMunicipio = apps.get_model('ibge', 'IndicadorMunicipio')
    FatoIndicador = apps.get_model('ibge', 'FatoIndicador')
    Tempo = apps.get_model('ibge', 'Tempo')

    # Get all unique years from IndicadorMunicipio
    years = IndicadorMunicipio.objects.values_list('ano', flat=True).distinct()
    
    # Create Tempo records for each year
    year_to_tempo = {}
    for year in years:
        tempo, created = Tempo.objects.get_or_create(
            ano=year,
            mes=None,
            trimestre=None
        )
        year_to_tempo[year] = tempo
    
    # Migrate all data from IndicadorMunicipio to FatoIndicador
    fato_indicadores_to_create = []
    for indicador_municipio in IndicadorMunicipio.objects.all():
        tempo = year_to_tempo[indicador_municipio.ano]
        
        fato_indicador = FatoIndicador(
            municipio=indicador_municipio.municipio,
            indicador=indicador_municipio.indicador,
            tempo=tempo,
            valor=indicador_municipio.valor,
            criado_em=indicador_municipio.criado_em,
        )
        fato_indicadores_to_create.append(fato_indicador)
    
    # Bulk create for performance
    FatoIndicador.objects.bulk_create(fato_indicadores_to_create, batch_size=1000)


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - delete FatoIndicador records created by this migration.
    """
    FatoIndicador = apps.get_model('ibge', 'FatoIndicador')
    FatoIndicador.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ibge', '0016_fato_indicador'),
    ]

    operations = [
        migrations.RunPython(migrate_indicador_municipio_to_fato, reverse_migration),
    ]
