import logging
import requests

from django.core.management.base import BaseCommand

from ibge.models import Estado

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Sincroniza os estados do IBGE"

    def handle(self, *args, **kwargs):

        url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

        try:

            logger.info("[sync_estados] Sincronização iniciada")

            response = requests.get(url, timeout=10)

            response.raise_for_status()

            estados = response.json()

            criados = 0

            for estado in estados:

                _, created = Estado.objects.get_or_create(
                    codigo_externo=estado["id"],
                    sigla=estado["sigla"],
                    defaults={
                        "nome": estado["nome"],
                        "regiao": estado["regiao"]["nome"],
                    },
                )

                if created:
                    criados += 1

            logger.info(
                "[sync_estados] Recebidos=%s Criados=%s",
                len(estados),
                criados,
            )

        except requests.RequestException as e:

            logger.exception(
                "[sync_estados] erro=%s",
                str(e)
            )