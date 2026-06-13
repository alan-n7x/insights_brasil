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

        # 🔥 mapa otimizado (string normalizada)
        municipios_map = {
            str(m.codigo_externo): m
            for m in Municipio.objects.all()
        }

        series = data[0]["resultados"][0]["series"]

        total_salvos = 0

        with transaction.atomic():  # 🔥 performance + consistência

            for item in series:

                codigo = item["localidade"]["id"]
                serie = item["serie"]

                municipio = municipios_map.get(codigo)

                if not municipio:
                    continue

                # pega ano mais recente de forma segura
                ano = max(serie.keys())
                populacao = serie[ano]

                PopulacaoMunicipio.objects.update_or_create(
                    municipio=municipio,
                    ano=int(ano),
                    defaults={
                        "populacao": int(populacao)
                    }
                )

                total_salvos += 1

                logger.info(
                    "[sync_populacao] salvo municipio=%s codigo=%s ano=%s pop=%s",
                    municipio.nome,
                    codigo,
                    ano,
                    populacao,
                )

        fim = time.perf_counter()

        logger.info(
            "[sync_populacao] FINALIZADO municipios=%s tempo=%.2fs",
            total_salvos,
            fim - inicio,
        )