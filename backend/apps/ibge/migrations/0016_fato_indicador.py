# Generated migration for FatoIndicador model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ibge', '0015_enrich_indicador'),
    ]

    operations = [
        migrations.CreateModel(
            name='FatoIndicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=4, max_digits=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('indicador', models.ForeignKey(db_index=True, on_delete=models.CASCADE, related_name='fato_valores', to='ibge.indicador')),
                ('municipio', models.ForeignKey(db_index=True, on_delete=models.CASCADE, related_name='fato_indicadores', to='ibge.municipio')),
                ('tempo', models.ForeignKey(db_index=True, on_delete=models.CASCADE, related_name='fato_indicadores', to='ibge.tempo')),
            ],
            options={
                'verbose_name': 'Fato Indicador',
                'verbose_name_plural': 'Fatos Indicadores',
                'ordering': ['municipio', 'indicador', '-tempo'],
            },
        ),
        migrations.AddIndex(
            model_name='fatoindicador',
            index=models.Index(fields=['indicador', 'tempo'], name='ibge_fato_indicador_indicador_tempo_idx'),
        ),
        migrations.AddIndex(
            model_name='fatoindicador',
            index=models.Index(fields=['municipio', 'indicador'], name='ibge_fato_indicador_municipio_indicador_idx'),
        ),
        migrations.AddIndex(
            model_name='fatoindicador',
            index=models.Index(fields=['municipio', 'tempo'], name='ibge_fato_indicador_municipio_tempo_idx'),
        ),
        migrations.AddConstraint(
            model_name='fatoindicador',
            constraint=models.UniqueConstraint(fields=['municipio', 'indicador', 'tempo'], name='uniq_fato_indicador'),
        ),
    ]
