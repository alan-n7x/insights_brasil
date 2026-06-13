from django.shortcuts import render

# Create your views here.
import requests

from django.http import JsonResponse


def estados(request):

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    response = requests.get(url)

    return JsonResponse(
        response.json(),
        safe=False
    )