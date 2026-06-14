import logging
import requests
import time

from django.core.management.base import BaseCommand

from ibge.models import Estado, Municipio

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Sincroniza municípios do IBGE"

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_municipios] Sincronização iniciada")

        url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

        try:

            response = requests.get(url, timeout=30)

            response.raise_for_status()

            municipios = response.json()

            criados = 0
            ignorados = 0

            for municipio in municipios:

                try:

                    microrregiao = municipio.get("microrregiao")

                    if not microrregiao:

                        ignorados += 1

                        logger.warning(
                            "[sync_municipios] Município sem microrregião "
                            "id=%s nome=%s",
                            municipio["id"],
                            municipio["nome"],
                        )

                        continue

                    codigo_estado = municipio["microrregiao"]["mesorregiao"]["UF"]["id"]

                    estado = Estado.objects.get(codigo_externo=codigo_estado)

                    _, created = Municipio.objects.get_or_create(
                        codigo_externo=municipio["id"],
                        defaults={
                            "nome": municipio["nome"],
                            "estado": estado,
                        },
                    )

                    if created:
                        criados += 1

                    else:
                        ignorados += 1

                except Estado.DoesNotExist:

                    ignorados += 1

                    logger.warning(
                        "[sync_municipios] Estado não encontrado "
                        "municipio=%s codigo=%s",
                        municipio.get("nome"),
                        municipio.get("id"),
                    )

                except Exception:

                    ignorados += 1

                    logger.exception(
                        "[sync_municipios] erro municipio=%s codigo=%s",
                        municipio.get("nome"),
                        municipio.get("id"),
                    )

            fim = time.perf_counter()

            logger.info(
                "[sync_municipios] FINALIZADO "
                "recebidos=%s "
                "criados=%s "
                "ignorados=%s "
                "tempo=%.2fs",
                len(municipios),
                criados,
                ignorados,
                fim - inicio,
            )

        except requests.RequestException:

            logger.exception("[sync_municipios] erro ao consultar API do IBGE")
