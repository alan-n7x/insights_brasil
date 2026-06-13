import logging
from django.shortcuts import render

# Create your views here.
import requests

from django.http import JsonResponse
from .models import Estado

logger = logging.getLogger("ibge.views")


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
                sigla=estado["sigla"],
                defaults={
                    "nome": estado["nome"],
                    "regiao": estado["regiao"]["nome"],
                },
            )

            if created:
                criados += 1

        # logger.info(
        #     "Sincronização concluída. Recebidos=%s Criados=%s",
        #     len(estados),
        #     criados,
        # )

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
