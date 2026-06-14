import logging, time
from django.shortcuts import render

# Create your views here.
import requests

from django.http import JsonResponse
from ..models import Estado, Municipio

logger = logging.getLogger(__name__)


def estados(request):

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    response = requests.get(url)

    return JsonResponse(response.json(), safe=False)


def sync_estados(request):

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

        logger.info("[sync_estados] Recebidos=%s Criados=%s", len(estados), criados)

        return JsonResponse(
            {
                "status": "success",
                "total_recebidos": len(estados),
                "criados": criados,
            }
        )

    except requests.RequestException as e:

        logger.error(f"Erro ao consultar API do IBGE: {str(e)}")

        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=500,
        )


def sync_municipios(request):

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    try:

        logger.info("[sync_municipios] Sincronização iniciada")

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        municipios = response.json()

        criados = 0

        inicio = time.time()

        for municipio in municipios:

            try:

                microrregiao = municipio.get("microrregiao")

                if not microrregiao:

                    logger.warning(
                        f"[sync_municipios] Município sem microrregião: {municipio['id']} - {municipio['nome']}"
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

            except Estado.DoesNotExist:

                logger.warning(
                    f"[sync_municipios] Estado não encontrado para município "
                    f"{municipio['id']} - {municipio['nome']}"
                )

            except Exception as e:

                logger.error(
                    f"[sync_municipios] Erro ao processar município "
                    f"{municipio.get('id')} - {municipio.get('nome')}: {e}"
                )

                continue

        fim = round(time.time() - inicio, 2)

        logger.info(
            f"[sync_municipios] Recebidos={len(municipios)} "
            f"Criados={criados} "
            f"Tempo={fim}s"
        )

        return JsonResponse(
            {
                "status": "success",
                "recebidos": len(municipios),
                "criados": criados,
            }
        )

    except requests.RequestException as e:

        logger.error(f"[sync_municipios] Erro ao consultar API: {str(e)}")

        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=500,
        )
