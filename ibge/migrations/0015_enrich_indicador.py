# Generated migration to enrich Indicador model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ibge', '0014_tempo'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicador',
            name='descricao',
            field=models.TextField(blank=True, help_text='Descrição detalhada do indicador'),
        ),
        migrations.AddField(
            model_name='indicador',
            name='unidade',
            field=models.CharField(blank=True, help_text='Unidade de medida (ex: habitantes, R$ milhões, índice)', max_length=50),
        ),
        migrations.AddField(
            model_name='indicador',
            name='periodicidade',
            field=models.CharField(blank=True, help_text='Periodicidade dos dados (ex: Anual, Mensal, Trimestral)', max_length=30),
        ),
        migrations.AddField(
            model_name='indicador',
            name='fonte',
            field=models.CharField(blank=True, help_text='Fonte dos dados (ex: IBGE/SIDRA)', max_length=100),
        ),
        migrations.AddField(
            model_name='indicador',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='indicador',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
