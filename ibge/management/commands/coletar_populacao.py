import time
import logging
import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from ibge.models import Municipio, PopulacaoMunicipio

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Coleta população dos municípios (IBGE)"

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_populacao] Iniciando coleta")

        url = (
            "https://servicodados.ibge.gov.br/api/v3/agregados/6579/"
            "periodos/-1/variaveis/9324?localidades=N6[all]"
        )

        r = requests.get(url, timeout=60)

        logger.info(
            "[sync_populacao] IBGE status=%s tamanho=%s",
            r.status_code,
            len(r.text),
        )

        data = r.json()

        municipios_map = {
            str(m.codigo_externo): m
            for m in Municipio.objects.all()
        }

        series = data[0]["resultados"][0]["series"]

        total_criados = 0
        total_atualizados = 0
        total_ignorados = 0

        with transaction.atomic():

            for item in series:

                codigo = item["localidade"]["id"]
                serie = item["serie"]

                municipio = municipios_map.get(codigo)

                if not municipio:
                    total_ignorados += 1
                    continue

                ano = max(serie.keys())
                populacao = int(serie[ano])

                obj, created = PopulacaoMunicipio.objects.get_or_create(
                    municipio=municipio,
                    ano=int(ano),
                    defaults={"populacao": populacao}
                )

                if not created and obj.populacao != populacao:
                    obj.populacao = populacao
                    obj.save(update_fields=["populacao"])
                    total_atualizados += 1

                elif created:
                    total_criados += 1

                else:
                    total_ignorados += 1

                logger.info(
                    "[sync_populacao] municipio=%s codigo=%s ano=%s pop=%s",
                    municipio.nome,
                    codigo,
                    ano,
                    populacao,
                )

        fim = time.perf_counter()

        logger.info(
            "[sync_populacao] FINALIZADO criados=%s atualizados=%s ignorados=%s tempo=%.2fs",
            total_criados,
            total_atualizados,
            total_ignorados,
            fim - inicio,
        )